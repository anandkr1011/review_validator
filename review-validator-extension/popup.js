let actionBtn = document.getElementById("actionBtn");

actionBtn.addEventListener("click", async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: extractReviewHelpful,
  });
});

function extractReviewHelpful() {
  const elements = document.querySelectorAll("._3c3Px5"); // .3c3Px5 is class for the review section page for like/dislike on flipkart
  const TempArr = Array.from(elements).map((elements) => elements.textContent); // like/dislike

  const ReviewUsefulArr = [];
  const ReviewNotUsefulArr = [];
  const netUsefullReviewArr = [];
  const ratingsArray = [];
  TempArr.forEach((value, index) => {
    if (index % 2 === 0) {
      // index 0
      ReviewUsefulArr.push(value);
    } else {
      ReviewNotUsefulArr.push(value); // index 1
    }
  });

  // netUsewful = like  - dislike
  ReviewUsefulArr.forEach((value, index) => {
    let netNum = ReviewUsefulArr[index] - ReviewNotUsefulArr[index];
    if (netNum >= 0) {
      netUsefullReviewArr[index] = netNum;
    } else {
      netUsefullReviewArr[index] = 0;
    }
  });

  const RevTextsElements = document.querySelectorAll(".t-ZTKy div div"); // for text
  const RevTextArray = Array.from(RevTextsElements).map(
    (RevTextsElements) => RevTextsElements.textContent // object -> text for all review object
  );

  const ratingElements = document.querySelectorAll("._3LWZlK._1BLPMq"); // for rating (0-9)

  ratingElements.forEach((ratingElement) => {
    const text = ratingElement.textContent;
    const ratingNumber = text.replace(/[^0-9]/g, ""); // if it is not number then replay with empty
    ratingsArray.push(ratingNumber);
  });

  // we create a json object that contains : reviewText, rating, reviewUseful
  const data = {
    rev_text: RevTextArray,
    rating: ratingsArray,
    review_useful: netUsefullReviewArr,
  };

  // fetching our django server with POST method that return review as 0/1
  // 0 -> fake, 1 - genuine
  fetch("http://127.0.0.1:8080/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data.review_status);
      const ReviewElements = document.querySelectorAll("._27M-vq"); // it is all review section/page

      // here we are scripting the review page with 2 diffrent colour ( 1-green / 0-red )
      let counter = 0; // index for the response array
      ReviewElements.forEach((select) => {
        if (data.review_status[counter] == 1) {
          color = "#afffaf";
        } else {
          color = "#ff9e9e";
        }
        select.style.backgroundColor = color;

        counter++;
      });
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

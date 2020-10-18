"use strict";
let serverUrl = "http://localhost:5000";

const get_summary = async (title) => {
  const route = `https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=${title}&origin=*`;
  fetch(route)
    .then((res) => res.json())
    .then((res) => {
      const pageId = Object.keys(res.query.pages)[0];
      // console.log(res.query.pages[pageId].extract);
      let summary = res.query.pages[pageId].extract;
      summary = summary.substr(0, 400) + "...";
      document.getElementById(title).innerText = summary;
      document.getElementById(title).classList.remove("loading-grad");
    });
};

let handleSearch = (e) => {
  e.preventDefault();
  let cb = document.getElementById("advanced");
  let flag;
  if (cb.checked)
    flag = "true";
  else
    flag = "false";
  console.log(flag);
  let searchParams = {
    advanced: flag,
    query: document.getElementsByClassName("search-input")[0].value,
  };
  let url = new URL(serverUrl + "/api/search-results");
  url.search = new URLSearchParams(searchParams).toString();
  fetch(url)
    .then((res) => {
      if (res.ok) {
        // Change search bar position
        let changeInitStyle = Array.from(
          document.getElementsByClassName("init")
        );
        for (let element of changeInitStyle) {
          element.classList.remove("init");
        }
      }
      return res.json();
    })
    .then((data) => {
      // Clear previous results
      document.getElementsByClassName("search-results-container")[0].innerHTML =
        "";
      if (data.length == 0) {
        document.getElementsByClassName(
          "search-results-container"
        )[0].innerHTML = "<h2>No Results</h2>";
      } else {
        data.forEach((result) => {
          let resultItem = document.createElement("div");
          resultItem.className = "result-item";
          // Use data from result once API is complete
          let title = result[2];
          get_summary(title);
          let resultLink = result[3];
          resultItem.innerHTML = `<a href="${resultLink}"><h2>${title}</h2><small>${resultLink}</small></a><p id="${title}" class="summary loading-grad"></p><hr/>`;
          document
            .getElementsByClassName("search-results-container")[0]
            .appendChild(resultItem);
        });
      }
    });
};

document
  .getElementsByClassName("search-form")[0]
  .addEventListener("submit", handleSearch);

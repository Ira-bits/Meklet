"use strict";
let serverUrl = "http://localhost:5000";

let handleSearch = (e) => {
    e.preventDefault();
    let searchParams = {
        advanced: "false",
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
            document.getElementsByClassName(
                "search-results-container"
            )[0].innerHTML = "";
            if (data.length == 0) {
                document.getElementsByClassName(
                    "search-results-container"
                )[0].innerHTML = "<h2>No Results</h2>";
            } else {
                data.forEach((result) => {
                    let resultItem = document.createElement("div");
                    resultItem.className = "result-item";
                    // Use data from result once API is complete
                    let title = "Temp Result";
                    let resultLink = "./";
                    let summary = result[1].toString();
                    resultItem.innerHTML =
                        '<h3><a href ="' +
                        resultLink +
                        '">' +
                        title +
                        "</a></h3>" +
                        "<p>" +
                        summary +
                        "</p>" +
                        "<hr/>";
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

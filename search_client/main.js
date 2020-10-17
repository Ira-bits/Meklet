"use strict";
document.getElementsByClassName("search-button")[0].onclick = () => {
    let searchQuery = {
        queryText: document.getElementsByClassName("search-input")[0].value,
    };
    // fetch(url, {
    //     body: searchQuery,
    // }).then((res) => {
    //     console.log(res);
    //     if (res.ok) {
    //         let changeInitStyle = Array.from(
    //             document.getElementsByClassName("init")
    //         );
    //         console.log(changeInitStyle);
    //         for (let element of changeInitStyle) {
    //             console.log(element);
    //             element.classList.remove("init");
    //         }
    //     }
    // });
};

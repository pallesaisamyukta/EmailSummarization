function showLoading() {
  // Create a div element for the loading indicator
  var loadingDiv = document.createElement("div");
  loadingDiv.id = "loading";
  loadingDiv.style.position = "fixed";
  loadingDiv.style.top = "50%";
  loadingDiv.style.left = "50%";
  loadingDiv.style.transform = "translate(-50%, -50%)";

  // Create a spinner element
  var spinner = document.createElement("div");
  spinner.classList.add("spinner-border", "text-primary");
  spinner.style.width = "3rem";
  spinner.style.height = "3rem";

  // Append the spinner to the loading div
  loadingDiv.appendChild(spinner);

  // Append the loading div to the body
  document.body.appendChild(loadingDiv);
}

function hideLoading() {
  // Remove the loading indicator from the DOM
  var loadingDiv = document.getElementById("loading");
  if (loadingDiv) {
    loadingDiv.remove();
  }
}

document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    console.log("Username: " + username);
    console.log("Password: " + password);

    // Show loading indicator
    showLoading();

    // Make a POST request to 127.0.0.1:8000/summarize with "email" and "password" in JSON request body
    fetch("http://127.0.0.1:8000/summarize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: username,
        password: password,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Hide loading indicator
        hideLoading();

        // Show alert with response data
        alert(JSON.stringify(data));
      })
      .catch((error) => {
        // Hide loading indicator
        hideLoading();

        console.error("Error:", error);
        // Show error alert
        alert("An error occurred. Please try again later.");
      });
  });

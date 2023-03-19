console.log("Sanity check!");

// Get Stripe publishable key
fetch("/config/")
  .then((result) => {
    console.log(result.json)
    return result.json();
  })
  .then((data) => {
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);

    // new
    // Event handler
    document.querySelector("#createCheckout").addEventListener("click", () => {
      // Get Checkout Session ID
      console.log("inside");
      // let loadingBtn = document.getElementById("loadingBtn");
    
      // loadingBtn.classList.remove("d-none");
      fetch("/create-checkout-session/")
        .then((result) => {
          console.log("result", result);
          return result.json();
        })
        .then((data) => {
          console.log(data);
          // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({ sessionId: data.sessionId });
        })
        .then((res) => {
          console.log(res);
        });
    });
  });

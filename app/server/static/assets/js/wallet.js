async function connectWallet(walletType) {
  switch (walletType) {
    case "metamask":
      connectMetaMask();
      break;
    // case "trustwallet":
    // case "binancewallet":
    //     connectInjectedWallet();
    //     break;
    // case "walletconnect":
    //     connectWalletConnect();
    //     break;

    default:
      alert("Unsupported wallet type!");
      console.error("Unsupported wallet:", walletType);
  }
}

async function connectMetaMask() {
  if (window.ethereum) {
      try {
          const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });

          if (!accounts || accounts.length === 0) {
              alert("No wallet found in MetaMask. Please create or import a wallet before connecting.");
              return;
          }

          const userWallet = accounts[0];
          updateUI(userWallet);
          sendWalletToBackend(userWallet);
          verifyWallet(userWallet);

      } catch (error) {
          alert(error.message || "MetaMask connection failed. Try again.");
          console.error("MetaMask error:", error);
      }
  } else {
      alert("MetaMask not detected! Install it first.");
  }
}


// ✅ UI Update Function
// function updateUI(walletAddress) {
//   document.getElementById("wallet-address").innerText = `Connected: ${walletAddress}`;
//   localStorage.setItem("walletAddress", walletAddress);
// }

async function sendWalletToBackend(walletAddress) {
  try {
    const response = await fetch("/update_wallet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wallet_address: walletAddress }),
    });
    const data = await response.json();
    console.log("Wallet stored:", data);
  } catch (error) {
    console.error("Error sending wallet to backend:", error);
  }
}

async function verifyWallet(walletAddress) {
  try {
    const response = await fetch("/verify_wallet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address: walletAddress }),
    });
    const data = await response.json();
    const statusElement = document.getElementById("wallet-status");

    if (data.status === "success") {
      statusElement.innerText = "✅ Wallet verified!";
      statusElement.style.color = "green";
    } else {
      statusElement.innerText = "❌ Invalid wallet!";
      statusElement.style.color = "red";
    }
  } catch (error) {
    console.error("Error verifying wallet:", error);
  }
}

// Auto-connect wallet if stored in session
async function checkWalletStatus() {
  if (window.ethereum && localStorage.getItem("walletAddress")) {
    try {
      const accounts = await window.ethereum.request({
        method: "eth_accounts",
      });
      if (accounts.length > 0) {
        document.getElementById(
          "wallet-address"
        ).innerText = `Connected: ${accounts[0]}`;
        verifyWallet(accounts[0]);
      }
    } catch (error) {
      console.error("Error checking wallet status:", error);
    }
  }
}
window.addEventListener("load", checkWalletStatus);

// async function depositToGasFee() {
//   const recipient = document.getElementById("gasfee-eth-address").innerText;
//   const amount = document.querySelector(".gasfeeDeposit__form-input").value;

//   if (!recipient || !amount || parseFloat(amount) <= 0) {
//       alert("Please enter a valid deposit amount.");
//       return;
//   }

//   try {
//       console.log("Depositing to Gas Fee account...");
//       const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
//       const sender = accounts[0];

//       const transactionParameters = {
//           from: sender,
//           to: recipient,
//           value: window.ethereum.utils.toHex(window.ethereum.utils.toWei(amount, "ether")),
//           gasPrice: await window.ethereum.request({ method: "eth_gasPrice" })
//       };

//       const txHash = await window.ethereum.request({
//           method: "eth_sendTransaction",
//           params: [transactionParameters]
//       });

//       alert(`Transaction Sent! Tx Hash: ${txHash}`);
//       console.log("Gas Fee Deposit Transaction Hash:", txHash);

//       // ✅ Update UI & Store Deposit in Backend
//       updateGasFeeBalance();
//       sendGasDepositToBackend(sender, amount);

//   } catch (error) {
//       alert("Deposit failed. Please check your wallet.");
//       console.error("Gas Fee Deposit Error:", error);
//   }
// }

// async function updateGasFeeBalance() {
//   try {
//       const accounts = await window.ethereum.request({ method: "eth_accounts" });
//       const userWallet = accounts[0];

//       const balance = await window.ethereum.request({
//           method: "eth_getBalance",
//           params: [userWallet, "latest"]
//       });

//       document.querySelector(".gasfeeDeposit__wallet-balance h1 strong").innerText = `${(parseInt(balance, 16) / 1e18).toFixed(4)} ETH`;

//   } catch (error) {
//       console.error("Error fetching Gas Fee balance:", error);
//   }
// }

// // ✅ Call this function whenever a deposit is successful
// window.addEventListener("load", updateGasFeeBalance);


// async function sendGasDepositToBackend(walletAddress, amount) {
//   try {
//       const response = await fetch("/wallet/gasfee_deposit", {  // ✅ Corrected endpoint
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ wallet_address: walletAddress, amount: amount })
//       });

//       const data = await response.json();
//       console.log("Gas Fee Deposit stored:", data);

//   } catch (error) {
//       console.error("Error sending gas fee deposit to backend:", error);
//   }
// }

// window.addEventListener("load", updateGasFeeBalance);


// async function depositToWallet() {
//   const recipient = document.getElementById("eth-address").value;
//   const amount = document.querySelector(".walletDeposit__form-input").value;

//   if (!recipient || !amount || parseFloat(amount) <= 0) {
//       alert("Please enter a valid deposit amount.");
//       return;
//   }

//   try {
//       console.log("Depositing to Main Wallet...");
//       const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
//       const sender = accounts[0];

//       const transactionParameters = {
//           from: sender,
//           to: recipient,
//           value: window.ethereum.utils.toHex(window.ethereum.utils.toWei(amount, "ether")),
//           gasPrice: await window.ethereum.request({ method: "eth_gasPrice" })
//       };

//       const txHash = await window.ethereum.request({
//           method: "eth_sendTransaction",
//           params: [transactionParameters]
//       });

//       alert(`Transaction Sent! Tx Hash: ${txHash}`);
//       console.log("Wallet Deposit Transaction Hash:", txHash);

//       // ✅ Update Wallet Balance & Backend Database
//       updateWalletBalance();
//       sendWalletDepositToBackend(sender, amount);

//   } catch (error) {
//       alert("Deposit failed. Please check your wallet.");
//       console.error("Wallet Deposit Error:", error);
//   }
// }

// async function updateWalletBalance() {
//   try {
//       const accounts = await window.ethereum.request({ method: "eth_accounts" });
//       const userWallet = accounts[0];

//       const balance = await window.ethereum.request({
//           method: "eth_getBalance",
//           params: [userWallet, "latest"]
//       });

//       document.querySelector(".walletDeposit__wallet-balance h1 strong").innerText = `${(parseInt(balance, 16) / 1e18).toFixed(4)} ETH`;

//   } catch (error) {
//       console.error("Error fetching Wallet balance:", error);
//   }
// }


// // ✅ Call this function whenever a deposit is successful
// window.addEventListener("load", updateWalletBalance);
// async function sendWalletDepositToBackend(walletAddress, amount) {
//   try {
//       const response = await fetch("/wallet/wallet_deposit", {  // ✅ Corrected endpoint
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ wallet_address: walletAddress, amount: amount })
//       });

//       const data = await response.json();
//       console.log("Wallet Deposit stored:", data);

//   } catch (error) {
//       console.error("Error sending wallet deposit to backend:", error);
//   }
// }

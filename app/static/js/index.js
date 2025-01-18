const loginText = document.querySelector(".title-text .login");
const loginForm = document.querySelector("form.login");
const loginBtn = document.querySelector("label.login");
const signupBtn = document.querySelector("label.signup");
const signupLink = document.querySelector("form .signup-link a");

signupBtn.onclick = (() => {
  loginForm.style.marginLeft = "-50%";
  loginText.style.marginLeft = "-50%";
});

loginBtn.onclick = (() => {
  loginForm.style.marginLeft = "0%";
  loginText.style.marginLeft = "0%";
});

signupLink.onclick = (() => {
  signupBtn.click();
  return false;
});

document.querySelector("form.login").addEventListener("submit", function(event) {
  const email = document.querySelector(".login input[type='text']").value;
  const password = document.querySelector(".login input[type='password']").value;
  if (!email || !password) {
    event.preventDefault();  
    alert("Please fill in all fields.");
  }
});

document.querySelector("form.signup").addEventListener("submit", function(event) {
  const firstName = document.querySelector(".signup input[name='first_name']").value;
  const lastName = document.querySelector(".signup input[name='last_name']").value;
  const email = document.querySelector(".signup input[name='email']").value;
  const password = document.querySelector(".signup input[name='password']").value;
  const confirmPassword = document.querySelector(".signup input[name='confirm_password']").value;

  if (!firstName || !lastName || !email || !password || !confirmPassword) {
    event.preventDefault();  
    alert("Please fill in all fields.");
  } else if (password !== confirmPassword) {
    event.preventDefault();
    alert("Passwords do not match.");
  }
});

setTimeout(function() {
  var flashContainer = document.querySelector('.flash-container');
  if (flashContainer) {
    flashContainer.remove(); 
  }
}, 3000); 


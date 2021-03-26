function showPw() {
    var x = document.getElementById("signuppw");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
  }
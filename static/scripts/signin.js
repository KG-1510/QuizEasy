function showPw() {
    var x = document.getElementById("loginpw");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
  }

$("#file-upload").css("opacity", "0");

$("#file-browser").click(function (e) {
  e.preventDefault();
  $("#file-upload").trigger("click");
});

const fileInput = document.querySelector(
  "input[type=file]"
);
fileInput.onchange = () => {
  if (fileInput.files.length > 0) {
    const fileName = document.querySelector(".file-name");
    const uploadedFileName = fileInput.files[0].name;
    document.querySelector('.choose-file-label').style.display = "none";
    fileName.textContent = uploadedFileName;

    if(uploadedFileName.includes(".pdf")){
      document.querySelector(".pdf").classList.add('pdficon')
      document.querySelector(".txt").classList.remove('txticon')
    }
    
    else if(uploadedFileName.includes(".txt")){
      document.querySelector(".txt").classList.add('txticon')
      document.querySelector(".pdf").classList.remove('pdficon')
    
    }
  }
};

function encryptInput() {
    // Read user input
    var input = document.getElementById("InputField").value;
    
    // Encrypt the input (example encryption logic)
    // var encrypted = "";
    // for (var i = 0; i < input.length; i++) {
    //   encrypted += String.fromCharCode(input.charCodeAt(i) + 1);
    // }
    input += 'a'
    // Set the input value to the form's input field
    document.getElementById("FORM").elements["msg"].value = input;
      
    // Submit the form
    document.getElementById("FORM").submit();
    // Display the encrypted output
    //document.getElementById("encryptedOutput").innerText = "Encrypted: " + encrypted;
    //return encrypted;
  }
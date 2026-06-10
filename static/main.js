// ================= SCHOOL ERP MAIN JS =================

console.log("School ERP Loaded Successfully 🚀");

// ================= ALERT ON DELETE =================
function confirmDelete() {
    return confirm("Are you sure you want to delete this student?");
}

// ================= FORM VALIDATION =================
function validateForm() {

    let name = document.getElementById("name").value;
    let fee = document.getElementById("fee").value;

    if (name === "") {
        alert("Name is required!");
        return false;
    }

    if (fee <= 0) {
        alert("Fee must be greater than 0!");
        return false;
    }

    return true;
}

// ================= SHOW SUCCESS MESSAGE =================
function showMessage(message) {
    alert(message);
}

// ================= AUTO HIDE ALERT =================
setTimeout(function () {
    let alertBox = document.getElementById("alert");

    if (alertBox) {
        alertBox.style.display = "none";
    }

}, 3000);

// ================= PRINT RECEIPT =================
function printReceipt() {
    window.print();
}

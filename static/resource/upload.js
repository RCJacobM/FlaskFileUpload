const fileinput = document.getElementById("file")
const filename = document.getElementById("filename")
const submit = document.getElementById("submit")
const form = document.getElementById("form")
submit.addEventListener("click", () => {
    form.submit()
})

if (fileinput.files[0]){
    fileinput.value = ""
}

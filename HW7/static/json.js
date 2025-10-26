window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const teacher = params.get("teacher") || "未知教師";

  const teacherElem = document.getElementById("teachername");
  if(teacherElem) teacherElem.textContent = `${teacher} 老師，您好`;

  const h1 = document.getElementById("teacherHidden");
  const h2 = document.getElementById("teacherHiddenDel");
  if(h1) h1.value = teacher;
  if(h2) h2.value = teacher;
});
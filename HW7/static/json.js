window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const teacher = params.get("teacher") || "未知教師";
  const teacherElem = document.getElementById("teachername");
  if (teacherElem) teacherElem.textContent = `${teacher} 老師，您好`;

  const gradeForm = document.getElementById("gradeForm");
  const studentTable = document.getElementById("studentTable");
  const deleteBtn = document.getElementById("deleteBtn");
  let students = [];

  if(gradeForm){
    gradeForm.addEventListener("submit", e => {
      e.preventDefault();
      const sName = document.getElementById("student_name").value.trim();
      const sId = document.getElementById("student_id").value.trim();
      const sScore = document.getElementById("student_score").value.trim();

      if(students.some(s => s.id === sId)){
        alert("該學號已存在！");
        return;
      }

      students.push({ name: sName, id: sId, score: sScore });
      renderTable();
      gradeForm.reset();
    });
  }

  if(deleteBtn){
    deleteBtn.addEventListener("click", () => {
      const delId = document.getElementById("Delete_student_data").value.trim();
      const index = students.findIndex(s => s.id === delId);
      if(index !== -1){
        students.splice(index, 1);
        renderTable();
      } else {
        alert("查無此學號！");
      }
    });
  }

  function renderTable(){
    studentTable.innerHTML = "";
    students.forEach(s => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${s.name}</td><td>${s.id}</td><td>${s.score}</td>`;
      studentTable.appendChild(row);
    });
  }
});
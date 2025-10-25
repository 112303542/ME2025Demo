let teachers_data = []

fetch("users.json")
  .then(res => res.json())
  .then(data => {
    teachers_data = data;
    initPage();
  })
  .catch(err => console.error("載入 users.json 失敗：", err));

function initPage() {
  const loginForm = document.getElementById("loginForm");
  const gradeForm = document.getElementById("gradeForm");

  if(loginForm){
    loginForm.addEventListener("submit", e => {
      e.preventDefault();
      const acc = document.getElementById("input_1").value.trim();
      const pw = document.getElementById("teacherpw").value.trim();
      const msg = document.getElementById("loginMsg");

      const teacher = teachers_data.find(t => t.username === acc && t.password === pw);

      if(teacher){
        localStorage.setItem("teacherName", teacher.username);
        window.location.href = "Grades.html";
      }
      else msg.textContent = "帳號或密碼錯誤";
    });
  }
  if(gradeForm){
    const teacherNameElem = document.getElementById("teachername");
    const name = localStorage.getItem("teacherName") || "未知教師";
    teacherNameElem.textContent = `${name} 老師，您好`;

    const studentTable = document.getElementById("studentTable");
    const deleteBtn = document.getElementById("deleteBtn");
    let students = [];

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

    deleteBtn.addEventListener("click", () => {
      const delId = document.getElementById("Delete_student_data").value.trim();
      const index = students.findIndex(s => s.id === delId);
      if(index !== -1){
        students.splice(index, 1);
        renderTable();
      } 
      else alert("查無此學號！");
    });

    function renderTable(){
      studentTable.innerHTML = "";
      students.forEach(s => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${s.name}</td><td>${s.id}</td><td>${s.score}</td>`;
        studentTable.appendChild(row);
      });
    }
  }
}
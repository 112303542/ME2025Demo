let teachers_data = []

fetch("users.json")
  .then(res => res.json())
  .then(data => {
    teachers_data = data;
    initPage();
  })
  .catch(err => console.error("載入 users.json 失敗：", err));


'use strict';
// home
const TOKEN = '7174fa6f9d0f954a92d2a5852a7fc3bcaace7578';

const textAreaStagesGroups = document.querySelector('#stages_from_area');
const chkbxCreateTxt = document.querySelector('#create_txt');
const chkbxMatrixAndBinValsSwarco = document.querySelector('#binval_swarco');
const fileInput = document.querySelector('#config_file');
const btnSendRequest = document.querySelector('#send_conflicts_data');
const divCalculatedContent = document.querySelector('#calculated_content');


//work
// const TOKEN = 'a090474ab50a6ec440eef021295d5f0e750afa00';
// const TOKEN = 'fb682e5942fa8ce5c26ab8cd3e8eaba41c4cd961'; shared_desktop

// Ловим событие изменения состояния radio типов дк
$('input[type=radio][name=controller_type]').change(function() {
  if ($('#undefind').is(':checked')) {
      $('#make_config').prop('checked', false);
      $('#binval_swarco').prop('checked', false);
      $('#binval_swarco').attr('disabled', true);
      $('#make_config').attr('disabled', true);
      $('#config_file').attr('disabled', true);   
  }
  else if ($('#swarco').is(':checked')) {
      $('#binval_swarco').attr('disabled', false);
      $('#make_config').attr('disabled', false);      
  }
  else {
      $('#binval_swarco').attr('disabled', true);
      $('#make_config').attr('disabled', false);
      $('#binval_swarco').prop('checked', false);
  }; 
});

// Ловим событие изменения чекбокса Создать файл конфигурации
$('#make_config').change( function() {
  if ($(this).is(':checked')){
    $('#config_file').attr('disabled', false);
  }
  else {
      $('#config_file').attr('disabled', true);
    };
    
});

// При нажатии на кнопку выбор файлов, установим необходимое раширение(для выбранного типа ДК) в браузере
$('#config_file').click( function (){
  if ($('#swarco').is(':checked')) {
    $(this).attr('accept', '.PTC2');
  }
  else if ($('#peek').is(':checked')){
    $(this).attr('accept', '.DAT');
  }

});


// Проверка валидности введенных/заполненных данных
// $("#send_conflicts_data").click(function () {
//   const text_area = {
//     text: $('#stages_from_area').val(),
//     lines: $('#stages_from_area').val().split('\n'),
//     num_lines: $('#stages_from_area').val().split('\n').length,
//   };

//   sendRequestToCalculate();
//   console.log(`text_area: <${text_area}>`)
//   console.log(`text_area.text: <${text_area.text}>`)
//   console.log(`text_area.lines: <${text_area.lines}>`)
//   console.log(`text_area.num_lines: <${text_area.num_lines}>`)

//   return;

//   if (text_area.num_lines < 2) {
//     alert('Количество фаз не может быть менее 2');
//     return false;
//   }

//   // Проверка на корректность символов
//   if (!check_text_area(text_area.lines)){
//     return false;
//   }
 
//   // Проверка на количество фаз
//   if (($('#swarco').is(':checked') && text_area.num_lines > 8)) {
//     alert(`Количество фаз для Swarco не должно превышать 8. Вы ввели: ${text_area.num_lines}`);
//     return false;
//   }
//   else if (($('#peek').is(':checked') && text_area.num_lines > 32)) {
//     alert(`Количество фаз для Peek не должно превышать 32. Вы ввели: ${text_area.num_lines}`);
//     return false;
//   }

//   else if (text_area.num_lines > 128) {
//     alert(`Количество фаз для неопределённого типа ДК не должно превышать 128. Вы ввели: ${text_area.num_lines}`);
//     return false;
//   }

//   // Проверка валидности данных при условии что выбран чекбокс "Создать файл конфигурации"
//   if ($('#make_config').is(':checked')) {
//     // Проверка на наличие файла
//     if ($('#config_file')[0].files.length < 1) {
//       alert('Вы не выбрали файл конфигурации');
//       return false;
//     }
//     // Проверка на корректное расширение файла для каждого типа ДК
//     let file_name = $('#config_file')[0].files[0].name;
//     if ($('#swarco').is(':checked') && file_name.slice(-5).toUpperCase() != '.PTC2'){
//       alert('Вы выбрали неверный формат файла конфигурации для Swarco. Выберите файл с раширением .PTC2');
//       return false;
//     }
//     else if ($('#peek').is(':checked') && file_name.slice(-4).toUpperCase() != '.DAT'){
//       alert('Вы выбрали неверный формат файла конфигурации для Peek. Выберите файл с раширением .DAT');
//       return false;
//     }
//   }
  
// });



// Проверка всего поля text_area на валидные символы


function check_text_area (stages) {
  for (let i = 0; i < stages.length; i++) {
    if (!check_string(stages[i], i + 1)) {
      return false;
    }
  }
  return true;

}
// Проверка строки на валидные символы
function check_string (stage_string, num_string, sep1=':', sep2=',') {
  if (stage_string.includes(sep1)) {
    stage_string = stage_string.replace(' ', '').split(sep1)[1];
  }
  let isNumber_last_char = /^\d+$/.test(stage_string.slice(-1));
  if (!isNumber_last_char) {
    alert(`Строка должна заканчиваться числовым номером направления. Проверьте строку ${num_string}`);
    return false;
  }
  let splited_string = stage_string.replace(' ', '').split(sep2);
  for(let ii = 0; ii < splited_string.length; ii++) {  
    let isNumber = /^\d+$/.test(splited_string[ii]);
    if (!isNumber) {
      alert(`Вы ввели не число в строке ${num_string}`);
      return false; 
    }
    else if (isNumber && (+splited_string[ii] > 128)) {
      alert(`Количество направлений не должно превышать 128. Вы ввели: ${splited_string[ii]} в строке ${num_string}`);
      return false;
    }
  }
  return true;
}


btnSendRequest.addEventListener('click', sendRequestToCalculate);
async function sendRequestToCalculate(event) {
  // const fileInput = document.querySelector('#config_file').files;
  console.log('config_file');
  let create_config;
  const form_data = new FormData();
  if (fileInput.files.length) {
    form_data.append('file', fileInput.files[0]);
    create_config = true;
  }
  else {
    create_config = false;
  }
  
  const data = {
    stages: textAreaStagesGroups.value,
    type_controller: document.querySelector('input[name="controller_type"]:checked').value,
    create_config: create_config,
    create_txt: chkbxCreateTxt.checked,
    swarco_vals: chkbxMatrixAndBinValsSwarco.checked,
  }
  form_data.append('data', JSON.stringify(data));

  const csrfToken = $("input[name=csrfmiddlewaretoken]").val();
  try {
      const responce = await axios.post('/api/v1/conflicts/', 
        form_data,
        {
          headers: {
              "X-CSRFToken": csrfToken, 
              "Content-Type": "multipart/form-data",
              "Authorization": `Bearer ${TOKEN}`,
          }
      });
      console.log(responce.data);
      writeCalculatedContent(responce.data);
  } catch (error) {
      if (error.response) { // get response with a status code not in range 2xx
        console.log(error.response.data);
        console.log(error.response.status);
        console.log(error.response.headers);
      } else if (error.request) { // no response
        console.log(error.request);
      } else { // Something wrong in setting up the request
        console.log('Error', error.message);
      }
      console.log(error.config); 
    }
    fileInput.value = null;
    
}

function writeCalculatedContent (responce) {
  clearElement(divCalculatedContent);

  // addUrlsforDownload(responce);

  
  divCalculatedContent.append(createTableOutputMatrix(responce.base_matrix));
}

function addUrlsforDownload (responce) {
  if (responce.txt_file != 'undefined') {
    const p = document.createElement('p');
    const link = document.createElement('a');
    link.setAttribute('href', responce.txt_file.url_to_file);
    link.setAttribute('download', '');
    link.textContent = `Скачать текстовый файл с расчётами`;
    divCalculatedContent.append(p);
    divCalculatedContent.append(link);
  }
}

function clearElement(element) {
  element.innerHTML = "";
}

// Формирует table(#output_matrix) матрицу конфликтов общего вида
function createTableOutputMatrix(matrix) {
  const table = document.createElement('table');
  table.setAttribute('id', 'output_matrix');
  let tr, cell;
  matrix.forEach((line_matrix, ind, arr) => {
    tr = document.createElement('tr');
    line_matrix.forEach((el, i, arr) => {
      if (ind === 0) {
        cell = document.createElement('th');
      }
      else {
        cell = (i > 0) ? document.createElement('td') : document.createElement('th');
      }
      cell = createCellMatrixOutput({
        value: el,
        element: cell,
      });
      tr.append(cell);
    });
    table.append(tr);
  });
  return table;
  
}

// Устанавливает значение и bg-color для td таблицы-матрицы конфликтов 
function createCellMatrixOutput(obj) {
  let value, element, content;
  element = obj.element;
  value = obj.value.replaceAll("|", "");
  if (value.includes('K')) {
    content = 'K';
    element.style.backgroundColor  = 'red';
  }
  else if (value.includes('O')) {
    content = 'O';
    element.style.backgroundColor  = 'green';
  }
  else if (Number.isInteger(+value)) {
    content = value;
  }
  else {
    content = '*';
  }
  element.textContent = content
  return element;
}

'use strict';

/*------------------------------------------------------------------------
|                            Старт страницы                              |
------------------------------------------------------------------------*/

$(document).ready(function(){

});


/*------------------------------------------------------------------------
|                                Константы                               |
------------------------------------------------------------------------*/

// home
const TOKEN = '7174fa6f9d0f954a92d2a5852a7fc3bcaace7578';
//work
// const TOKEN = 'a090474ab50a6ec440eef021295d5f0e750afa00';
//shared_desktop
// const TOKEN = 'fb682e5942fa8ce5c26ab8cd3e8eaba41c4cd961';
const ROUTE_API_TLC = `/api/v1/potok-tlc/`;

const input_condition = document.querySelector('#condition');
const idTableTokensFunctions = 'table_functions';
let   tableTokensFunctions = document.querySelector(`#${idTableTokensFunctions}`);
const btn_create_buttons = document.querySelector('#create_functions');
const btn_check_condition = document.querySelector(`#check_condition`);
// const table_create_functions = document.querySelector('#table_functions');


/*------------------------------------------------------------------------
|                               Events                                   |
------------------------------------------------------------------------*/

btn_create_buttons.addEventListener('click', getFunctionsFromConditionAxios);
btn_check_condition.addEventListener('click', createDataForCheckCondition);


 /*------------------------------------------------------------------------
|                      Запрос в api и обработка запроса                   |
--------------------------------------------------------------------------*/

// Отправка запроса команды с помощью библиотеки axios
async function getFunctionsFromConditionAxios(event) {

  const condition = input_condition.value;
  console.log('condition: '+ condition);
  
  let csrfToken = $("input[name=csrfmiddlewaretoken]").val();
  try {

      const response = await axios.post(ROUTE_API_TLC,          
          { 
            options: [],
            condition: condition,
          },
          {  
            headers: {
            "X-CSRFToken": csrfToken, 
          //   
            "Authorization": `Token ${TOKEN}`
            }
          }
      );

    const res = response.data;

    createTableFunctions(res);


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
      
    }

    finally {
      
    }
}

// Общая функция для обработки responce и формирования контента на странице


 /*------------------------------------------------------------------------
|            Запись полученых на странице в различные элементы            |
--------------------------------------------------------------------------*/

 /*------------------------------------------------------------------------
|   Создать таблицу с функциями из строки условия перехода/продления      |
--------------------------------------------------------------------------*/

// Создает <table> с функциями, полученными из строки "Условие перехода/продления"
function createTableFunctions (response) {
  console.log(response);
  const tokensFunctions = response.result;
  const len_tr = Math.sqrt(tokensFunctions.length);
  // Если повторное нажатие на кнопку "Сформировать функции и условия", удаляем имеющуюся таблицу и формируем новую

  console.log(tableTokensFunctions);
  if (tableTokensFunctions !== null) {
    tableTokensFunctions.remove()
  }
  tableTokensFunctions = document.createElement('table');
  tableTokensFunctions.setAttribute('id', idTableTokensFunctions);

  let tr, td, chkbx, label;
  tr = document.createElement('tr');

  tokensFunctions.forEach((element, index, array) => {  
  td = document.createElement('td');
  chkbx = document.createElement('input');
  label = document.createElement('label');

  if (Math.floor(index % len_tr) == 0) {
    tableTokensFunctions.append(tr);
    tr = document.createElement('tr');
  }

  chkbx.setAttribute('type', 'checkbox');
  chkbx.id = element;
  label.setAttribute('for', element);
  label.innerHTML = element;

  td.append(chkbx);
  td.append(label);
  tr.append(td);
  });

  tableTokensFunctions.append(tr);
  console.log(tableTokensFunctions);  
  btn_create_buttons.after(tableTokensFunctions);
}

function createDataForCheckCondition() {
  let dataReq = {condition: input_condition.value};
  let conditionWithFuncValues = input_condition.value
  console.log(document.querySelectorAll(`#${idTableTokensFunctions} td`));
  document.querySelectorAll(`#${idTableTokensFunctions} td`).forEach((el) => {
    console.log('elem text --> ' + el.textContent);
    console.log('elem id --> ' + el.firstChild.id);
    console.log('elem  firstChild --> ' + el.firstChild);
    console.log('elem firstChild.checked  --> ' + el.firstChild.checked);
    if (el.firstChild.id != el.textContent) {
      alert('Произошла ошибка в расчёте. Нажмите еще раз копку "Сформироват функции из условия"')
      return false;
    }
    dataReq[el.textContent] = el.firstChild.checked;
    conditionWithFuncValues = conditionWithFuncValues.replace(el.textContent, Number(el.firstChild.checked));

  });
  dataReq.conditionValues = conditionWithFuncValues;
  console.log(dataReq);
}
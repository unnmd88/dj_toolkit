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
const btn_create_buttons = document.querySelector('#create_functions');
// const table_create_functions = document.querySelector('#table_functions');


/*------------------------------------------------------------------------
|                               Events                                   |
------------------------------------------------------------------------*/

btn_create_buttons.addEventListener('click', getFunctionsFromConditionAxios);


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

    createTable(res);


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

function createTable (response) {
  console.log(response);
  
  const table = document.createElement('table');
  table.setAttribute('id', 'table_functions');
  // const tr = document.createElement('tr');
  
  // const td1 = document.createElement('td');
  // td1.textContent = 'fdfsdfs';
  // tr.appendChild(td1);
  // td1.innerText = 'iufh8sdgfowkfd';
  // tr.append(td1);
  // table.append(tr);
  // input_condition.append(table);

  const tokens = response.result;

  let len_tr = Math.sqrt(tokens.length);
  let tr = document.createElement('tr');
  tokens.forEach((element, index, array) => {
    console.log(Math.floor(index/len_tr));
    if (Math.floor(index % len_tr) == 0) {
      console.log(Math.floor(index/len_tr));
      table.append(tr);
      tr = document.createElement('tr');
    }

  
  console.log(len_tr);
  let td = document.createElement('td');
  let chkbx = document.createElement('input');
  chkbx.setAttribute('type', 'checkbox');
  chkbx.id = element;
  

  let label = document.createElement('label');
  label.setAttribute('for', element);
  label.innerHTML = element;
  label.append(chkbx);
  td.append(label);

  // td.textContent = element;
  tr.append(td);
  });
  table.append(tr);

  // for (let i = 0; i < 3; i++) {
  //   let tr = document.createElement('tr');
    
  //   for (let i = 0; i < 3; i++) {
  //     let td = document.createElement('td');
  //     td.textContent = 'tRTG'
  //     tr.append(td);
  //   }
    
  //   table.append(tr);

  // }
  let p = document.createElement('p');
  let br = document.createElement('br');
  // btn_create_buttons.after(p);
  // btn_create_buttons.after(p);
  btn_create_buttons.after(br);
  btn_create_buttons.after(table);

}
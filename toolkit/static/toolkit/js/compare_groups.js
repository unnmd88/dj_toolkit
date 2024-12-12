'use strict';

/*------------------------------------------------------------------------
|                            Старт страницы                              |
------------------------------------------------------------------------*/

$(document).ready(function(){
  document.querySelector('#table_groups').placeholder = placeholderTableGroups;
  document.querySelector('#table_stages').placeholder = placeholderTableStages;
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
const ROOT_ROUTE_API = '/api/v1/'
const ROOT_ROUTE_API_COMPARE_GROUPS = `/api/v1/compare-groups/`;

const placeholderTableGroups = `В данное поле скопируйте содержимое трёх колонок "Таблицы направлений" из паспорта объекта:
"№ нап.", "Тип направления", "Фазы, в кот. участ. направ.
Важно! Необходимо копировать содержимое напрямую из паспорта.
Пример:\n
1	Транспортное	1,2,6
2	Транспортное	1,2,3,6
3	Общ. трансп.	1,2,3,6
4	Транспортное	1,2,3,4,6
5	Поворотное	1,2
6	Пешеходное	1,2,3,6
7	Транспортное	4,5
8	Пешеходное	4,5
9	Пешеходное	4,5
10	Пешеходное	3,6
11	Пешеходное	5
12	Транспортное	Пост. красное`; 
const placeholderTableStages = `В данное поле скопируйте содержимое двух колонок "Программа x" из паспорта объекта:
"№ фазы", "Направления"
Важно! Необходимо копировать содержимое напрямую из паспорта.
Пример:\n
1	1,2,3,4,5,6
2	1,2,3,4,5,6
3	2,3,4,6,10
4	4,7,8,9
5	7,8,9,11
6	1,2,3,4,6,10`;


// Отправка запроса команды с помощью библиотеки axios
async function compare_groups_axios(event) {

    const content_table_groups = document.querySelector(`#table_groups`).value;
    const content_table_stages = document.querySelector(`#table_stages`).value;
                                                       
    let csrfToken = $("input[name=csrfmiddlewaretoken]").val();
    try {

        const response = await axios.post(ROOT_ROUTE_API_COMPARE_GROUPS,          
            {
              content_table_groups: content_table_groups,
              content_table_stages: content_table_stages
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
        console.log('response.data');
        console.log(response.data);
        displayResultCompareGroups(response.data);

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
        // button.removeAttribute('disabled');  
      }
}

const calculate = document.querySelector('#calculate');
calculate.addEventListener('click', compare_groups_axios);


 /*------------------------------------------------------------------------
|                        Запись полученых данных в дисплей                 |
--------------------------------------------------------------------------*/

// Функция форирует таблицу направлений с результатами сравнения
function displayResultCompareGroups (responce_data) {
  const div = document.querySelector('#main_div');
  const groups_info = responce_data.compare_groups.groups_info;
  const table_result = document.querySelector('#table_result');
  const num_cols = table_result.rows[0].cells.length;
  const rows = document.querySelectorAll('#table_result tr');
  
  const userDataIsValid = responce_data.compare_groups.error_in_user_data;
  remove_rows(table_result, rows.length, 1);
  
  if (typeof userDataIsValid === 'string') {
    alert('Проверьте корректность данных:\n' + userDataIsValid);
    return false;
  }

  for (const group in groups_info) {
    table_result.append(create_row_content(num_cols, group, groups_info[group]));
  }
}

// Удаляет все строки 
function remove_rows(table, rows_length, row_num_start) { 
  if (rows_length > row_num_start) {
    for (let i=rows_length-row_num_start; i>=row_num_start; i--) {
      table.deleteRow(i);
    }
  }
}

// Функция формирует строку с контентом для таблицы table_result(результат сравнения групп)
function create_row_content(num_cols, num_group, group_content) {

  let tr = document.createElement('tr');

  let td_num_group = document.createElement('td');
  let td_type_group = document.createElement('td');
  let td_stages = document.createElement('td');
  let td_errors = document.createElement('td');
  td_errors.setAttribute("class", "errors_content");

  td_num_group.textContent = num_group;
  td_type_group.textContent = group_content.type_group;
  td_stages.textContent = group_content.stages;
  const errors = group_content.errors;
  if (errors.length > 0) {
    errors.forEach((element, idx) => {
      td_errors.innerHTML += `${idx + 1}. ${element}`  + '<br>';
      td_errors.setAttribute("background-color", "red");
    });
  }

  tr.append(td_num_group);
  tr.append(td_type_group);
  tr.append(td_stages);
  tr.append(td_errors);
  return tr;
}

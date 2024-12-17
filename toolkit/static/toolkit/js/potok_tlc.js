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
// const TOKEN = '7174fa6f9d0f954a92d2a5852a7fc3bcaace7578';
//work
const TOKEN = 'a090474ab50a6ec440eef021295d5f0e750afa00';
//shared_desktop
// const TOKEN = 'fb682e5942fa8ce5c26ab8cd3e8eaba41c4cd961';
const ROOT_ROUTE_API = '/api/v1/'
const ROOT_ROUTE_API_COMPARE_GROUPS = `/api/v1/compare-groups/`;

const input_condition = document.querySelector('#condition');
const btn_create_buttons = document.querySelector('#create_functions');


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

      const response = await axios.post(ROOT_ROUTE_API_COMPARE_GROUPS,          
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

// Общая функция для обработки responce и формирования контента на странице


 /*------------------------------------------------------------------------
|            Запись полученых на странице в различные элементы            |
--------------------------------------------------------------------------*/


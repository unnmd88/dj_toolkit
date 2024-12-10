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


// Отправка запроса команды с помощью библиотеки axios
async function set_request_axios(event) {

    const content_table_groups = document.querySelector(`#table_groups`).value;
    const content_table_stages = document.querySelector(`#table_stages`).value;
                                                       
    let csrfToken = $("input[name=csrfmiddlewaretoken]").val();
    try {
        // display.textContent += '\n\nИдёт отправка команды...'
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
        // console.log('res[result]');
        // console.log(res['result']);

        console.log('response.data');
        console.log(response.data);      

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
        // console.log(error.config);
        // display.textContent += '\nКоманда не отправлена, сервер недоступен';
        
      }

      finally {
        // button.removeAttribute('disabled');  
      }
}

const calculate = document.querySelector('#calculate');
calculate.addEventListener('click', set_request_axios);

 /*------------------------------------------------------------------------
|                        Запись полученых данных в дисплей                 |
--------------------------------------------------------------------------*/




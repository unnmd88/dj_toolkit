'use strict';

/*------------------------------------------------------------------------
|                            Старт страницы                              |
------------------------------------------------------------------------*/

$(document).ready(function(){


});



/*------------------------------------------------------------------------
|                                Константы                               |
------------------------------------------------------------------------*/

const CONTROLLERS = ['Swarco', 'Поток (S)', 'Поток (P)', 'Peek']

//home
// const TOKEN = '7174fa6f9d0f954a92d2a5852a7fc3bcaace7578';
//work
const TOKEN = 'a090474ab50a6ec440eef021295d5f0e750afa00';
//shared_desktop
// const TOKEN = 'fb682e5942fa8ce5c26ab8cd3e8eaba41c4cd961';
const ROOT_ROUTE_API = '/api/v1/'
const ROOT_ROUTE_API_GET_TRAFFIC_LIGHT_OBJECT = '/api/v1/trafficlight-objects/'
const ROUTE_API_DOWNLOAD_CONFIG = `${ROOT_ROUTE_API}download-config/`;




// Отправка запроса команды с помощью библиотеки axios
async function set_request_axios(num_host) {

    const display = document.querySelector(`#displaySendCommand_${num_host}`);
    const button = document.querySelector(`#SetToHost_${num_host}`);
    button.setAttribute('disabled', true);

    let ip, type_controller, type_command, set_val, scn;
    let data_request = {};

    ip = `${$('#ip_' + num_host).val()}`;
    type_controller = `${$(`#protocol_${num_host} option:selected`).text()}`;
    type_command = `${$(`#setCommand_${num_host} option:selected`).text()}`;
    set_val = `${$('#setval_' + num_host).val()}`;
    scn = `${$(`#scn_${num_host}`).val()}`;
    

    data_request[ip] = {'host_id': num_host,
                       'type_controller':  type_controller,
                       'request_entity': {[type_command]: set_val},
                    //    'type_command': type_command,
                    //    'set_val': set_val,
                       'scn': scn
                       }  
                                                    
   // data_request[`${$('#ip_' + num_host).val()}`] = {
    //                                                 host_id: num_host,
    //                                                 type_controller:  `${$(`#protocol_${num_host} option:selected`).text()}`,
    //                                                 type_command: `${$(`#setCommand_${num_host} option:selected`).text()}`,
    //                                                 set_val: `${$('#setval_' + num_host).val()}`,
    //                                                 scn: `${$(`#scn_${num_host}`).val()}`
    // }  

    let csrfToken = $("input[name=csrfmiddlewaretoken]").val();
    try {
        display.textContent += '\n\nИдёт отправка команды...'
        const response = await axios.post(ROUTE_API_MANAGE_CONTROLLER,          
            {
              hosts: data_request,
              type_request: 'set'
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
        write_data_to_display_set(display, BASIC_DATA, res[ip], data_request[ip], num_host);
        display.scrollTop = display.scrollHeight;
        

        
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
        display.textContent += '\nКоманда не отправлена, сервер недоступен';
        
      }

      finally {
        button.removeAttribute('disabled');  
      }
}

 /*------------------------------------------------------------------------
|                        Запись полученых данных в дисплей                 |
--------------------------------------------------------------------------*/

// Запись в "дисплей" полученного состояния ДК(get request)

function write_data_to_display_get(display, type, data) {
    // Шапка, общая для всех "дисплеев"
    display.textContent += `\n\nВремя запроса: ${data.request_time}`;
    let content = '';
    if (data.request_errors) {
        content = `\nОшибка запроса: ${data.request_errors}`;
        // display.textContent  += `\nОшибка запроса: ${data.request_errors}`;
    }
    // BASIC_DATA -> общие данные о режиме"
    else if (type === BASIC_DATA) {
        // Отображение для контроллера Пик(с учётом количества потоков(xp))
        if (data.type_controller === CONTROLLERS[3]) {
            content = createContentPeekGet_Display(data);
        }
        // Отображение для контроллера для остальных типов дк
        else {
            content = `\nФаза=${data.responce_entity.raw_data.current_states.basic.current_stage} ` + 
                      `План=${data.responce_entity.raw_data.current_states.basic.current_plan} ` +
                      `Режим=${data.responce_entity.raw_data.current_states.basic.current_mode}`
        }                              
    }
    display.textContent += content;
}

function createContentPeekGet_Display(data_resp_json) {
    let content = '';
    if (typeof data_resp_json.responce_entity.raw_data.current_states.basic != 'undefined') {

        const basic = data_resp_json.responce_entity.raw_data.current_states.basic;
        const streams = basic.streams;
        
            content += `\nПлан=${data_resp_json.responce_entity.raw_data.current_states.basic.current_plan} `;
            for (let i = 1; i <= streams; i++) {
                const curr_stream = basic.stream_info[i.toString()];
                content += `\nПоток ${i}: ${curr_stream.current_state} ` +
                           `Фаза=${curr_stream.current_stage} `+
                           `Режим=${curr_stream.current_mode}`
            } 
        };
        console.log(content);
    return content;
}

 /*------------------------------------------------------------------------
|                               SEARCH HOST                                |
--------------------------------------------------------------------------*/




const search_input = document.querySelector('#search_controller');
search_input.addEventListener('input', search_host_get_data);

async function search_host_get_data(event) {

    console.log('search_host_get_data');
    
    const value = event.target.value;
    
    let response;
    try {
         response = await axios.get(            
            // `/api/v1/trafficlight-objects/${value}`,
            ROOT_ROUTE_API_GET_TRAFFIC_LIGHT_OBJECT + value,
            {
            headers: {
                "Authorization": `Token ${TOKEN}`,
            },
            },

        );
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
        console.log(error.config);
        response = error.response;

      } finally {
        write_data_about_host(response.data);
        check_valid_data_to_send_req(response.data);
      }
    
 }

 // Записывает данные в label теги,  полученные о СО
function write_data_about_host(data) {
    console.log('write_data_about_host');
    console.log(data);

    const content_elements = {
        ip_adress: document.querySelector('#ip_addr_val'),
        type_controller:document.querySelector('#type_controller_val'),
        adress: document.querySelector('#address_val'),
        description: document.querySelector('#description_val')
    }

    for (let key in content_elements) {
        content_elements[key].textContent = data[key] ? data[key]: ''
        }
    
}

// Проверка типа контроллера. Если Swarco, включить кнопку "Отправить запрос"



function check_valid_data_to_send_req(data) {
    if (data.type_controller === CONTROLLERS[0]) {
        console.log(data);
        document.querySelector('#get_config').disabled = false;
    }
    else {
        document.querySelector('#get_config').disabled = true;
    }
}

const btnDownloadConfig = document.querySelector('#get_config');
btnDownloadConfig.addEventListener('click', download_config);

// Функция отправки зароса на загрузку конфига
async function download_config(event) {
  console.log('download_configППП');
  document.querySelector('#search_controller').value
  try {
      const response = await axios.post(            
        ROUTE_API_DOWNLOAD_CONFIG,
        {
          // hosts: {[document.querySelector('#ip_addr_val').textContent]: {"host_id": "", "type_controller": "Swarco"}},
          hosts: collectDataForRequset(),
          type_request: 'get_config'
        },
          {
          headers: {
              "Authorization": `Token ${TOKEN}`,
          },
          },

      );
      console.log('response.data');
      console.log(response.data);
      
      const div = document.querySelector('#main_data')
      for (const ipAddr in response.data) {
        let file_name = Object.keys(response.data[ipAddr].responce_entity.url_to_archive)[0];
        // file_name = file_name[0];
        console.log(file_name);
        // console.log(file_name);
        // console.log(Object.keys(response.data[ipAddr].responce_entity.url_to_archive)[0]);
        const url_to_file =  response.data[ipAddr].responce_entity.url_to_archive[file_name];
        
        const p = document.createElement('p');
        const link = document.createElement('a');
        link.setAttribute('href', url_to_file);
        link.textContent = `Скачать ${file_name}`;
        div.append(p);
        div.append(link);
      }


      // get_config.insertAdjacentHTML('afterend', link);
      // document.querySelector('#get_config').after(link);


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
  
}

function collectDataForRequset(type_data='fromDB') {

  const hosts = {};
  let ipAddr, type_controller, host_id, address;
  if (type_data === 'fromDB') {
    ipAddr = document.querySelector('#ip_addr_val').textContent;
    type_controller = document.querySelector('#type_controller_val').textContent;
    address = document.querySelector('#address_val').textContent;
    host_id = document.querySelector('#search_controller').value;

  }
  else if (type_data === 'fromUser') {
    ipAddr = document.querySelector('#ip_controller').value;
    const select_type_controller = document.querySelector('#type_controller_from_user');
    type_controller = select_type_controller.options[select_type_controller.selectedIndex].text;
    host_id = "";
  }

  hosts[ipAddr] = {
    host_id: host_id,
    request_entity:['get_config'],
    type_controller: type_controller,
    address: address
  }
  console.log(hosts);
  return hosts;
}




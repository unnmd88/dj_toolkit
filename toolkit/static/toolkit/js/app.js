'use strict';

const intervalID = [false, false, false, false, false, false, false, false, false, false];
const chkbx = [getdatahost_1, getdatahost_2, getdatahost_3, getdatahost_4, getdatahost_5,
    getdatahost_6, getdatahost_7, getdatahost_8, getdatahost_9
];

// --------------GET REQUEST SNMP------------------
// Отслеживаем нажатие чекбокса, который отвечает за постоянный запрос данных с дк по snmp у хоста 1

// Создаем функции на изменения чекбокс внутри каждого хоста
for (let i=1; i < 11; i++) {
    console.log(`Это i: ${i}`)
    $(`#getdatahost_${i}`).change(function() {
        console.log(intervalID)
    
        console.log(`num_host = ${i}`)
    
        if (chkbx[i-1].checked && !intervalID[i]){
            let id_getData = setInterval(getData, 4000, i);
            intervalID[i] = id_getData;
    
        console.log('if');
    
        }
        else{
            clearInterval(intervalID[i])
            intervalID[i] = false;
        console.log('else');
        document.getElementById(`datahost_${i}`).textContent="--";
    
        }
        console.log(intervalID)
    
        }
    
    )
}

// Функция запроса и получения текущего режима/плана/фазы по snmp
let getData = function (num_host){

    console.log(num_host);
    $.ajax({

    type: "GET",
    url: `get-data-snmp/${num_host}/`,
    data:{
        'ip_adress': $('#ip_' + num_host).val(),
        'protocol': $(`#protocol_${num_host} option:selected`).text(),
        'scn': $(`#scn_${num_host}`).val(),
        },
    dataType: 'text',
    cache: false,
    success: function (data) {
    console.log(data)
    let postStringify = JSON.parse(data);
    console.log(postStringify);
    $(`#datahost_${num_host}`).text(`Фаза: ${postStringify.Фаза}, План: ${postStringify.План}, \n
                                    Режим: ${postStringify.Режим}  `);
                                    
    // $(`#datahost_${num_host}`).text(data);
    // document.getElementById(`datahost_${num_host}`).textContent=data;
    if (data == 'yes'){
    console.log(data);
    }
    else if (data == 'no'){
    }
        }
    }
);
}

// --------------SET REQUEST SNMP------------------
//Функция отправки запроса команды при нажатии кнопки
$("#SetToHost_1").click(function (){
    console.log('Tetss');
    $.ajax({

    type: "GET",
    url: "set_snmp_ajax/",
    data:{
        'ip_adress': $('#ip_1').val(),
        'protocol': $("#protocol_1 option:selected").text(),
        },

    dataType: 'text',
    cache: false,
    success: function (data) {
    console.log(data)
    const postStringify = JSON.parse(data)
    console.log(postStringify)

    if (data == 'yes'){
    console.log(data);
    }
    else if (data == 'no'){
    }
        }
    }
);
}
)




// Клик на #display_hosts_snmp -> Отображение количества хостов
$("#display_hosts_snmp").click( function() {
    show_hide_hosts_snmp();
    } 
)

// Функция отображения количества хостов
const show_hide_hosts_snmp = function () {
    console.log('ssssss')
    const select_visible_hosts = document.querySelector('#visible_hosts');
    const num_hosts_to_view = select_visible_hosts.value;
    console.log(`num_hosts_to_view -> ${num_hosts_to_view}`);

    for (let i=1; i < 10; i++) {
        if(i <= num_hosts_to_view) {
            $(`#table_${i}`).show();
        }
        else {
            $(`#table_${i}`).hide();
        }
        }
}

$(`#table_1`).show();



// function intUser(a,b) {
//   let i = setInterval(() => {
//     console.log(a++);
//     if (a > b) clearInterval(i);
//   }, 1000)
// }

// intUser(5, 10);





///////////////VARIABLES GLOBALES\\\\\\\\\\\\\\\\\
moment.lang('es', {
  months: 'Enero_Febrero_Marzo_Abril_Mayo_Junio_Julio_Agosto_Septiembre_Octubre_Noviembre_Diciembre'.split('_'),
  monthsShort: 'Enero._Feb._Mar_Abr._May_Jun_Jul._Ago_Sept._Oct._Nov._Dec.'.split('_'),
  weekdays: 'Domingo_Lunes_Martes_Miercoles_Jueves_Viernes_Sabado'.split('_'),
  weekdaysShort: 'Dom._Lun._Mar._Mier._Jue._Vier._Sab.'.split('_'),
  weekdaysMin: 'Do_Lu_Ma_Mi_Ju_Vi_Sa'.split('_')
}
);
var alertawarning = document.getElementById('alertawarning');
var data;
var fecha=document.getElementById("fecha");
var id=document.getElementById("id");
var modulo=document.getElementById("modulo");
var pedido=document.getElementById("pedido");
var HM=document.getElementById("HM");
var nombre=document.getElementById("nombre");
var gafete=document.getElementById("gafete");

function fechaActual(){
  let fecha = new Date();
  let mes = fecha.getMonth()+1;
  let dia = fecha.getDate()+1;
  let ano = fecha.getFullYear();
  if (dia<10) {
    dia = '0'+dia;
  }
  if (mes<10) {
    mes = '0'+mes;
  }
  document.getElementById('fechaf').value = ano+"-"+mes+"-"+dia;
  fechaAnterior(mes, dia, ano);
}
function fechaAnterior(mes, dia, ano){
let fechaInicial = document.getElementById('fechai');
let mesAnterior = mes.length === 1? mes-1: ("0"+ (mes-1)).slice(-2);
if (mesAnterior <1){
  mesAnterior =  12 + parseInt(mesAnterior)
  ano = ano-1
}
let DiaAnterior = dia.length === 1? dia : ("0" + dia).slice(-2);
fechaInicial.setAttribute("value", `${ano}-${mesAnterior}-${DiaAnterior}`);
}

var options = {
  Historial : ["Fecha","HM"],
  Login : ["Fecha","Nombre","Gafet"],
  Modulos_Fusibles : ["ID","Modulo"],
  Modulos_Torques : ["ID","Modulo"],
  Pedidos : ["Fecha","Pedido"],
  Usuarios : ["Fecha","Nombre","Gafet"]
}

$(function(){
var fillSecondary = function(){
  var selected = $('#selector').val();
  if ($('#selector').val() == "Log") {
    $('#tipo_busqueda').empty();
    $('#tipo_busqueda').css("display","none");
    $('#label_busqueda').css("display","none");
    fecha.style.display = 'inline-block';
    HM.style.display = 'none';
    nombre.style.display = 'none';
    gafete.style.display = 'none';
    id.style.display = 'none';
    modulo.style.display = 'none';
    pedido.style.display = 'none';
  }else{
    $('#tipo_busqueda').css("display","inline-block");
    $('#label_busqueda').css("display","inline-block");
    $('#tipo_busqueda').empty();
    options[selected].forEach(function(element,index){
      $('#tipo_busqueda').append('<option value="'+element+'">'+element+'</option>');
    });
  }
  switch ($('#tipo_busqueda').val()) {
    case "Fecha":
      // console.log("Búsqueda por FECHA")
      fecha.style.display = 'inline-block';
      HM.style.display = 'none';
      nombre.style.display = 'none';
      gafete.style.display = 'none';
      id.style.display = 'none';
      modulo.style.display = 'none';
      pedido.style.display = 'none';
    break;
    case "ID":
      // console.log("Búsqueda por id")
      fecha.style.display = 'none';
      HM.style.display = 'none';
      nombre.style.display = 'none';
      gafete.style.display = 'none';
      id.style.display = 'inline-block';
      modulo.style.display = 'none';
      pedido.style.display = 'none';
    break;
    default:
    break;
  }
}
var cambio = function(){
  switch ($('#tipo_busqueda').val()) {
    case "Fecha":
      // console.log("Búsqueda por FECHA")
      fecha.style.display = 'inline-block';
      HM.style.display = 'none';
      nombre.style.display = 'none';
      gafete.style.display = 'none';
      id.style.display = 'none';
      modulo.style.display = 'none';
      pedido.style.display = 'none';
    break;
    case "HM":
      // console.log("Búsqueda por HM")
      fecha.style.display = 'none';
      HM.style.display = 'inline-block';
      nombre.style.display = 'none';
      gafete.style.display = 'none';
      id.style.display = 'none';
      modulo.style.display = 'none';
      pedido.style.display = 'none';
      document.getElementById("hminput").focus();
    break;
    case "Nombre":
      // console.log("Búsqueda por Nombre")
      fecha.style.display = 'none';
      HM.style.display = 'none';
      nombre.style.display = 'inline-block';
      gafete.style.display = 'none';
      id.style.display = 'none';
      modulo.style.display = 'none';
      pedido.style.display = 'none';
      document.getElementById("nombreinput").focus();
    break;
    case "Gafet":
      // console.log("Búsqueda por Gafet")
      fecha.style.display = 'none';
      HM.style.display = 'none';
      nombre.style.display = 'none';
      gafete.style.display = 'inline-block';
      id.style.display = 'none';
      modulo.style.display = 'none';
      pedido.style.display = 'none';
      document.getElementById("gafeteinput").focus();
    break;
    case "ID":
      // console.log("Búsqueda por id")
      fecha.style.display = 'none';
      HM.style.display = 'none';
      nombre.style.display = 'none';
      gafete.style.display = 'none';
      id.style.display = 'inline-block';
      modulo.style.display = 'none';
      pedido.style.display = 'none';
    break;
    case "Modulo":
      // console.log("Búsqueda por modulo")
      fecha.style.display = 'none';
      HM.style.display = 'none';
      nombre.style.display = 'none';
      gafete.style.display = 'none';
      id.style.display = 'none';
      modulo.style.display = 'inline-block';
      pedido.style.display = 'none';
      document.getElementById("moduloinput").focus();
    break;
    case "Pedido":
      // console.log("Búsqueda por Pedido")
      fecha.style.display = 'none';
      HM.style.display = 'none';
      nombre.style.display = 'none';
      gafete.style.display = 'none';
      id.style.display = 'none';
      modulo.style.display = 'none';
      pedido.style.display = 'inline-block';
      document.getElementById("pedidoinput").focus();
    break;  
    default:
    break;
  }
}
$('#selector').change(fillSecondary);
fillSecondary();
$('#tipo_busqueda').change(cambio);
cambio();
});



function cleardiv(){
  document.getElementById("resultado").innerHTML = "";
  document.getElementById("descarga").innerHTML = "";
}
// Función que se ejecuta al oprimir el botón "Obtener Resultados"
function capturar(){
  if (sessionStorage.getItem('tipo') == null) {
    alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">Necesita inicar sesión para visualizar esta información.</div>'
  } else {
    var tabla=document.getElementById("selector").value;
    // console.log(tabla);
    switch (tabla){
      case "Historial":
      cleardiv();
      cargarhistorial();
      console.log("Historial");
      break;
      case "Login":
      cleardiv();
      cargarportipo();
      console.log("Obtener Resultados de Login");
      break;
      case "Log":
      cleardiv();
      cargardatetime();
      console.log("Obtener Resultados de Log");
      break;
      case "Modulos_Alturas":
      cleardiv();
      cargarmodulo();
      console.log("Obtener Resultados de Modulos_Alturas");
      break;
      case "Modulos_Fusibles":
      cleardiv();
      cargarmodulo();
      console.log("Obtener Resultados de Modulos_Fusibles");
      break;
      case "Modulos_Torques":
      cleardiv();
      cargarmodulo();
      console.log("Obtener Resultados de Modulos_Torques");
      break;
      case "Pedidos":
      cleardiv();
      cargarpedido();
      console.log("Obtener Resultados de Pedidos");
      break;
      case "Usuarios":
      cleardiv();
      cargarportipo_usuarios();
      console.log("Obtener Resultados de Usuarios");
      break;
      default:
      console.log("No pasa nada");
    }
  }
}
//////////////// AL SELECCIONAR TABLAS QUE NECESITEN REALIZAR CONSULTAS EN BASE A "Datetime" SE EJECUTARÁ ESTA FUNCIÓN //////////////////////////////////
function cargardatetime(){
  console.log("Inicio"); 
  fetch(dominio+"/json2/"+document.getElementById('selector').value+"/datetime/>/"+document.getElementById('fechai').value+"/</"+document.getElementById('fechaf').value)
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';
    }

    var colnames = data.columns;
    var filas = data[colnames[0]].length;
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.classList.add('nowrap');
    table.cellSpacing="0";
    table.width="100%";
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    for (i = 0; i < colnames.length; i++) {
      var titulo = colnames[i].replace("_"," ")
      var th = document.createElement('TH')
      th.width = '100';
      th.appendChild(document.createTextNode(titulo));
      tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
       
        var td = document.createElement('TD')
        switch (colnames[j]){
          case "QR_BOXES":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-qrcode");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-qr');
          boton.style.width="60px"
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "MODULOS_VISION":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-modulosF');
            boton.style.width="60px"
            boton.appendChild(icono);
            td.appendChild(boton);
          break;
          case "MODULOS_ALTURA":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-modulosA');
            boton.style.width="60px"
            boton.appendChild(icono);
            td.appendChild(boton);
          break;
          case "MODULOS_TORQUE":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-modulosT');
            boton.style.width="60px"
            boton.appendChild(icono);
            td.appendChild(boton);
          break;
          default:
          td.appendChild(document.createTextNode(data[colnames[j]][i]));
        }
        tr.appendChild(td)
      } 
     
      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable({
        responsive:true
      });
    } );
  })
}

$(document).on('click','.btn-ver-qr', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/pedidos/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/pedidos/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
        let nav = document.createElement("nav");
        let caja = dataKeys[i];
        nav.id = "titulo-caja"
        nav.innerHTML = "<b>"+caja+"</b>";
        div.appendChild(nav);

        //console.log("Aqui esta la CAJA:",caja);
        let cavidades = dataParse[caja];
       // console.log("Aquí en object: ",cavidades)
       
        
        
        let grid = document.createElement("div");
        grid.classList = "grid-box";
        nav.appendChild(grid);
        
        let span = document.createElement("span");
        span.classlist = "caja-valor";
        span.innerHTML = `<p>${cavidades}</p>`;
        nav.appendChild(span);
     }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});

$(document).on('click','.btn-ver-estado', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/pedidos/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/log/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[header_info]);
      document.getElementById("informacion").innerHTML = data[header_info];
      $('#mostrar').click();
    })
  }
});

function cargarfecha(){
  fetch(dominio+"/json2/"+document.getElementById('selector').value+"/datetime/>/"+document.getElementById('fechai').value+"/</"+document.getElementById('fechaf').value)
  .then(data=>data.json())
  .then(data=>{
     console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';
    }

    var colnames = data.columns;
    // console.log(colnames);
    colnames.splice(colnames.indexOf("GAFET"),1);
    // console.log("Elemento eliminado",colnames.splice(2,1));
    // console.log("el nuevo array: ", colnames);
    var filas = data[colnames[0]].length;
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.classList.add('nowrap');
    table.cellSpacing="0";
    table.width="100%";
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
      th.width = '100';
      th.appendChild(document.createTextNode(colnames[i]));
      tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        td.appendChild(document.createTextNode(data[colnames[j]][i]));
        tr.appendChild(td)
      }
      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable({
        responsive:true
      });
    } );
  })
}

//////////////// AL SELECCIONAR LA TABLA "Historial" SE EJECUTARÁ ESTA FUNCIÓN PARA REALIZAR LA CONSULTA DE LOS DATOS A LA TABLA CORRESPONDIENTE ///////////////////////
function cargarhistorial(){
  if ($('#tipo_busqueda').val() == "HM") {
    var url = dominio+"/json2/historial/HM/=/"+document.getElementById('hminput').value+"/=/_";
  }else{
    url = dominio+"/json2/historial/inicio/>/"+document.getElementById('fechai').value+"/</"+document.getElementById('fechaf').value;
  }
  fetch(url)
  .then(data=>data.json())
  .then(data=>{
    historialApp(data);
  }
  )};






async function historialApp(data){
  try{
  const mostrar = await mostrarHistorial(data);
    console.log(mostrar);
  const descargar = await descargarHistorial(data);
  console.log(descargar);
    console.log('Tablas de descargas listas');
  }
  catch(error){
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';
      
    }
  }
}
   function mostrarHistorial(data){
    return new Promise( resovle => {
    var colnames = data.columns;
   // colnames.push("INTERVALO")
    colnames.splice(colnames.indexOf("INTERVALO"))
    colnames.splice(colnames.indexOf("USUARIO"),0 ,"INTERVALO")
    var filas = data[colnames[0]].length;
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.classList.add('nowrap');
    table.cellSpacing="0";
    table.width="100%";
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    colnames.push("OPERACION");
    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
      var titulo = colnames[i].replace("_"," ")
      th.width = '100';
      //console.log(colnames[i]);
      th.appendChild(document.createTextNode(titulo));
      tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        switch (colnames[j]){
          case "VISION":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-file-alt");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-vision');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "ALTURA":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-file-alt");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-altura');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "INTENTOS_VA":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-file-alt");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-intentosva');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "TORQUE":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-file-alt");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-torque');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "ANGULO":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-file-alt");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-angulo');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "INTENTOS_T":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-file-alt");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-intentost');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "SCRAP":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-file-alt");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-scrap');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          break;
          case "SERIALES":
          var boton = document.createElement('button');
          var icono = document.createElement('i');
          icono.classList.add("fas");
          icono.classList.add("fa-barcode");
          boton.title = "Ver Información";
          boton.classList.add('btn');
          boton.classList.add('btn-info');
          boton.classList.add('btn-ver-seriales');
          boton.style.width="60px";
          boton.appendChild(icono);
          td.appendChild(boton);
          var texto = document.createElement('p');
          texto.appendChild(document.createTextNode(data[colnames[j]][i]))
          texto.style.display = "none";
          td.appendChild(texto);
          break;
          case "NOTAS":
            var nota = data[colnames[j]][i];
            dataParse = JSON.parse(nota);
            //console.log("Convertido a JSON: ",dataParse)
            dataKeys = Object.keys(dataParse)
            //console.log("dataKeys: ",dataKeys.length)
            // td.appendChild(document.createTextNode(nota));
            var div = document.createElement('div')
            for (let title = 0; title < dataKeys.length; title++) {
              const col = dataKeys[title];
              //console.log(col)
              let nav = document.createElement('nav');
              nav.innerHTML = `<b>${col}: </b>`;
              div.appendChild(nav);
              
              for (let x = 0; x < dataParse[col].length; x++) {
                const noteValue = dataParse[col][x];
                let p = document.createElement('p');
                p.innerHTML = noteValue;
                nav.appendChild(p);
              }
              div.appendChild(nav); 
            }
            td.appendChild(div);
          break;
          case "OPERACION":
            if (data["RESULTADO"][i] === 2){
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-print");
            boton.title = "Imprimir";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-operacion');
            boton.value =  
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
          }
            else{
              td.appendChild(document.createTextNode("NO DISPONIBLE"))
            }
            break;
            case "INTERVALO":
            fecha_fin_hora = new Date(data["FIN"][i]).getUTCHours() 
            fecha_fin_min = new Date(data["FIN"][i]).getUTCMinutes()
            fecha_fin_seg = new Date(data["FIN"][i]).getUTCSeconds()
            
            fecha_inicio_hora =  new Date(data["INICIO"][i]).getUTCHours()
            fecha_inicio_min =  new Date(data["INICIO"][i]).getUTCMinutes()
            fecha_inicio_seg =  new Date(data["INICIO"][i]).getUTCSeconds()
           // console.log(fecha_fin_hora - fecha_inicio_hora, data["ID"][i]);

            // if (transcurridoMinutos < 0) {
            //   transcurridoHoras--;
            //   transcurridoMinutos = 60 + transcurridoMinutos;
            // }
            transcurridoMinutos = fecha_fin_min - fecha_inicio_min;
            //console.log(transcurridoMinutos)
            transcurridoHoras = fecha_fin_hora - fecha_inicio_hora;
            //console.log(transcurridoHoras)
            transcurridoSegundos = fecha_fin_seg - fecha_inicio_seg;
            //console.log(transcurridoSegundos)
            
            if (transcurridoMinutos < 0) {
              transcurridoHoras--;
              transcurridoMinutos = 60 + transcurridoMinutos;
            }
            if (transcurridoSegundos < 0) {
              transcurridoMinutos--;
              transcurridoSegundos = 60 + transcurridoSegundos;
            }
            
            horas = transcurridoHoras.toString();
            minutos = transcurridoMinutos.toString();
            segundos = transcurridoSegundos.toString();
            
            
            //console.log(horas+":"+minutos+" "+segundos);
            let diferencia = horas <= 0? `${minutos} Minutos, y ${segundos} Segundos`:`${horas} Hora(s), ${minutos} Minutos, y ${segundos} Segundos` ;
            td.appendChild(document.createTextNode(diferencia));
            break;
            default:
            td.appendChild(document.createTextNode(data[colnames[j]][i]));
            break;
        }
        
        tr.appendChild(td)
      }
      // console.log("Inicio",fecha_inicio, "Fin",fecha_fin); 
      // console.log("Difiere",fecha_inicio.from(fecha_fin), data["ID"][i]); 

      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable({
        responsive:true
      });
     });
    setTimeout( () => {
      resovle('Las Tablas fueron Descargadas');
  },1000);
  });
  };

  function descargarHistorial(data){
    return new Promise( resovle => {
    var colnames = data.columns;
    var filas = data[colnames[0]].length;
    //CREACIÓN DE TABLA PARA DESCARGAR HISTORIAL
    var myTableDiv_descarga = document.getElementById("descarga");
    var table_descarga = document.createElement('TABLE');
    var tableBody_descarga = document.createElement('TBODY');
    var Encabezados_descarga = document.createElement('THEAD');

    table_descarga.id = "myTable_descarga";
    table_descarga.classList.add('display');
    table_descarga.classList.add('nowrap');
    table_descarga.style.display = 'none';
    table_descarga.cellSpacing="0";
    table_descarga.width="100%";
    table_descarga.border = '2';
    table_descarga.appendChild(Encabezados_descarga);
    table_descarga.appendChild(tableBody_descarga);
    tableBody_descarga.align="center";
    //FIN DE CREACIÓN DE TABLA PARA DESCARGAR HISTORIAL

    //CREACION DE LA TABLA PARA DESCARGAR TORQUE
    let torque = [];
    let intentos_t = [];
    let vision = [];
    let altura = [];
    let intentos_va = [];
    let angulo = [];

    //ENCABEZADOS DE LA TABLA PARA DESCARGAR
    individuales= JSON.stringify(colnames);
    var tr = document.createElement('TR');
    Encabezados_descarga.appendChild(tr);
    colnames.splice(colnames.indexOf("VISION"),3); // Comentar en caso de querer descargar la tabla original y no sencilla
    // console.log("columnas: ",colnames);
    colnames.splice(colnames.indexOf("SERIALES"),1);
    colnames.splice(colnames.indexOf("RESULTADO"),0,("SERIALES"));
    colnames.splice(colnames.indexOf("SCRAP"),1);
    colnames.splice(colnames.indexOf("NOTAS"),0,("SCRAP"));
    //colnames.splice(colnames.indexOf("INTERVALO",1))
    colnames.splice(colnames.indexOf("TORQUE"),1);
    colnames.splice(colnames.indexOf("INTENTOS_VA"),1);
    colnames.splice(colnames.indexOf("INTENTOS_T"),1);
    colnames.splice(colnames.indexOf("ANGULO"),1);
    console.log(individuales); ///Conserva los nombres de los objetos originales

    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
      th.width = '100';
        th.appendChild(document.createTextNode(colnames[i]))
        tr.appendChild(th).style.backgroundColor="#0DBED6"; 
      };
    
      
      for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        let re = /null/g;
        let ul = document.createElement("ul");
        let colTitle;
        let boxTitle;
        switch(colnames[j]){
          case "SERIALES":
            // console.log("Seriales: ",data[colnames[j]][i]);
            let referencia = JSON.parse(data[colnames[j]][i]);
            // console.log("referencia+-+-+- ",referencia)
            // console.log(referencia['REF'])
            td.appendChild(document.createTextNode(referencia['REF']));
            break;
            case "NOTAS":
              colTitle = colnames[j];
              // console.log("Titulo: ",colnames[j]);
              // console.log("INTENTOS_T: ",data[colnames[j]][i]);
              dataParse = data[colTitle];
              //console.log(dataParse[i]);
              var cajas = JSON.parse(dataParse[i]);
              //console.log(cajas);
              boxTitle = Object.keys(cajas);
              //console.log(boxTitle);
              for (let x = 0; x < boxTitle.length; x++) {
                let li = document.createElement("li");
  
                const boxName = boxTitle[x];
                //console.log(boxName);// Titulo de la caja
                li.innerHTML = `<b>${boxName}<b>`;
                var boxCav = cajas[boxName];
                var elementos = Object.keys(cajas[boxName]); // Cantidades de datos la caja
  
                for (let y = 0; y < elementos.length; y++) {
                  let p = document.createElement("p");
                  const cavidad = elementos[y];
                  //console.log(`${cavidad}:${boxCav[cavidad]}`);
                  p.innerHTML = `&nbsp;${cavidad}:${boxCav[cavidad]}&nbsp;`;
                  li.appendChild(p);
                } 
                ul.appendChild(li);
              }
              td.appendChild(ul);
              // document.getElementById("informacion").appendChild(ul)
              break;
              case "SCRAP":
              colTitle = colnames[j];
              // console.log("Titulo: ",colnames[j]);
              // console.log("INTENTOS_T: ",data[colnames[j]][i]);
              dataParse = data[colTitle];
              //console.log(dataParse[i]);
              var cajas = JSON.parse(dataParse[i]);
              //console.log(cajas);
              boxTitle = Object.keys(cajas);
              //console.log(boxTitle);
              for (let x = 0; x < boxTitle.length; x++) {
                let li = document.createElement("li");
  
                const boxName = boxTitle[x];
                //console.log(boxName);// Titulo de la caja
                li.innerHTML = `<b>${boxName}<b>`;
                var boxCav = cajas[boxName];
                var elementos = Object.keys(cajas[boxName]); // Cantidades de datos la caja
  
                for (let y = 0; y < elementos.length; y++) {
                  let p = document.createElement("p");
                  const cavidad = elementos[y];
                  //console.log(`${cavidad}:${boxCav[cavidad]}`);
                  p.innerHTML = `&nbsp;${cavidad}:${boxCav[cavidad]}&nbsp;`;
                  li.appendChild(p);
                } 
                ul.appendChild(li);
              }
              td.appendChild(ul);
              // document.getElementById("informacion").appendChild(ul)
              break;
              case "INTERVALO":
            fecha_fin_hora = new Date(data["FIN"][i]).getUTCHours() 
            fecha_fin_min = new Date(data["FIN"][i]).getUTCMinutes()
            fecha_fin_seg = new Date(data["FIN"][i]).getUTCSeconds()
            
            fecha_inicio_hora =  new Date(data["INICIO"][i]).getUTCHours()
            fecha_inicio_min =  new Date(data["INICIO"][i]).getUTCMinutes()
            fecha_inicio_seg =  new Date(data["INICIO"][i]).getUTCSeconds()
           // console.log(fecha_fin_hora - fecha_inicio_hora, data["ID"][i]);

            // if (transcurridoMinutos < 0) {
            //   transcurridoHoras--;
            //   transcurridoMinutos = 60 + transcurridoMinutos;
            // }
            transcurridoMinutos = fecha_fin_min - fecha_inicio_min;
            //console.log(transcurridoMinutos)
            transcurridoHoras = fecha_fin_hora - fecha_inicio_hora;
            //console.log(transcurridoHoras)
            transcurridoSegundos = fecha_fin_seg - fecha_inicio_seg;
            //console.log(transcurridoSegundos)
            
            if (transcurridoMinutos < 0) {
              transcurridoHoras--;
              transcurridoMinutos = 60 + transcurridoMinutos;
            }
            if (transcurridoSegundos < 0) {
              transcurridoMinutos--;
              transcurridoSegundos = 60 + transcurridoSegundos;
            }
            
            horas = transcurridoHoras.toString();
            minutos = transcurridoMinutos.toString();
            segundos = transcurridoSegundos.toString();
            
            
            //console.log(horas+":"+minutos+" "+segundos);
            let diferencia = horas <= 0? `${minutos} Minutos, y ${segundos} Segundos`:`${horas} Hora(s), ${minutos} Minutos, y ${segundos} Segundos` ;
            td.appendChild(document.createTextNode(diferencia));
            break;
           case"FIN":
           let dateStamp = moment.utc((data[colnames[j]][i])).format("dddd, MMMM Do YYYY") +" a las "+ moment.utc((data[colnames[j]][i])).format("h:mm:ss a");
           // console.log(dateStamp)
           td.appendChild(document.createTextNode(dateStamp));
           break;
           case"INICIO":
           dateStamp_inicio = moment.utc((data[colnames[j]][i])).format("dddd, MMMM Do YYYY") +" a las "+ moment.utc((data[colnames[j]][i])).format("h:mm:ss a");
           td.appendChild(document.createTextNode(dateStamp_inicio));
           break;
            default:
            td.appendChild(document.createTextNode(data[colnames[j]][i]));
            break;

            }
        tr.appendChild(td)
      }
      tableBody_descarga.appendChild(tr);
    }
    myTableDiv_descarga.appendChild(table_descarga);
    
    const  colID = data[colnames[colnames.indexOf("ID")]];
        //FILAS DE LA TABLA PARA DESCARGAR
        for( i= 0; i < filas; i++){
          let secciones = JSON.parse(individuales);
          //console.log(data[secciones[i]]);
          for (j = 0; j < secciones.length; j++) {
         
            switch(secciones[j]){
              case "TORQUE":
                let columns = {};
                 colTitle = secciones[j];
                 //console.log(colID);
                 dataParse = data[colTitle];
                 //console.log(dataParse);
                 var cajas = dataParse[i] == false? "":JSON.parse(dataParse[i]);
                 var cajaKeys = Object.keys(cajas)
                 var arraySection = [];
                 for (let index = 0; index < cajaKeys.length; index++) {
                   let titleArray = cajaKeys[index]
                   let jsonString = JSON.stringify(cajas[cajaKeys[index]])
                   jsonString= jsonString.replace("{","")
                   jsonString= jsonString.split('"').join(' ');
                   jsonString= jsonString.replace("}"," ")
                   jsonString= jsonString.split("null").join('N/A ');
                   jsonString= jsonString.split("vacio").join('N/A ');
                   arraySection[titleArray] = jsonString;
                   columns = {...arraySection}
                  };                 
                 let ObjectID_TOR = { ID: colID[i], ...columns};
                 torque.push(ObjectID_TOR)
                 break;
                 case "ANGULO":
                let columns_ANG = {};
                 colTitle = secciones[j];
                 //console.log(colID);
                 dataParse = data[colTitle];
                 //console.log(dataParse);
                 var cajas = dataParse[i] == false? "":JSON.parse(dataParse[i]);
                 var cajaKeys = Object.keys(cajas)
                 var arraySection = [];
                  for (let index = 0; index < cajaKeys.length; index++) {
                    let titleArray = cajaKeys[index];
                    let jsonString = JSON.stringify(cajas[cajaKeys[index]])
                    jsonString= jsonString.replace("{","")
                    jsonString= jsonString.split('"').join(' ');
                    jsonString= jsonString.replace("}"," ")
                    jsonString= jsonString.split("null").join('N/A ');
                    jsonString= jsonString.split("vacio").join('N/A ');
                    arraySection[titleArray] = jsonString;
                    columns_ANG = {...arraySection}
                  };
                 let ObjectID_ANG = { ID: colID[i],...columns_ANG};
                 angulo.push(ObjectID_ANG)
                 break;
                 case "INTENTOS_VA":
                let columns_VA = {};
                 colTitle = secciones[j];
                 //console.log(colID);
                 dataParse = data[colTitle];
                 //console.log(dataParse);
                 var cajas = dataParse[i] == false? "":JSON.parse(dataParse[i]);
                 var cajaKeys = Object.keys(cajas)
                 var arraySection = [];
                  for (let index = 0; index < cajaKeys.length; index++) {
                    let titleArray = cajaKeys[index];
                    let jsonString = JSON.stringify(cajas[cajaKeys[index]])
                    jsonString= jsonString.replace("{","")
                    jsonString= jsonString.split('"').join(' ');
                    jsonString= jsonString.replace("}"," ")
                    jsonString= jsonString.split("null").join('N/A ');
                   jsonString= jsonString.split("vacio").join('N/A ');
                    arraySection[titleArray] = jsonString;
                    columns_VA = {...arraySection}
                  };
                 let ObjectID_VA = { ID: colID[i],...columns_VA};
                 intentos_va.push(ObjectID_VA)
                 break;
                 case "INTENTOS_T":
                   let columns_T = {};
                 colTitle = secciones[j];
                 //console.log(colID);
                 dataParse = data[colTitle];
                 //console.log(dataParse);
                 var cajas = dataParse[i] == false? "":JSON.parse(dataParse[i]);
                 var cajaKeys = Object.keys(cajas)
                 var arraySection = [];
                 for (let index = 0; index < cajaKeys.length; index++) {
                  let titleArray = cajaKeys[index];
                  let jsonString = JSON.stringify(cajas[cajaKeys[index]])
                   jsonString= jsonString.replace("{","")
                   jsonString= jsonString.split('"').join(' ');
                   jsonString= jsonString.replace("}"," ")
                   jsonString= jsonString.split("null").join('N/A ');
                   jsonString= jsonString.split("vacio").join('N/A ');
                   arraySection[titleArray] = jsonString;
                  columns_T = {...arraySection}
                };
                 let ObjectID_int_t = {ID: colID[i],...columns_T};
                 intentos_t.push(ObjectID_int_t)
                 break;
                 case "VISION":
                   let columns_V = {};
                 colTitle = secciones[j];
                 //console.log(colID);
                 dataParse = data[colTitle];
                 //console.log(dataParse);
                 var cajas = dataParse[i] == false? "":JSON.parse(dataParse[i]);
                 var cajaKeys = Object.keys(cajas)
                 var arraySection = [];
                 for (let index = 0; index < cajaKeys.length; index++) {
                  let titleArray = cajaKeys[index];
                  let jsonString = JSON.stringify(cajas[cajaKeys[index]])
                   jsonString= jsonString.replace("{","")
                   jsonString= jsonString.split('"').join(' ');
                   jsonString= jsonString.replace("}"," ")
                   jsonString= jsonString.split("null").join('N/A ');
                   jsonString= jsonString.split("vacio").join('N/A ');
                   arraySection[titleArray] = jsonString;
                  columns_V = {...arraySection}
                };
                 let ObjectID_vision = {ID: colID[i],...columns_V};
                 vision.push(ObjectID_vision)
                 break;
                 case "ALTURA":
                   let columns_A = {};
                 colTitle = secciones[j];
                 //console.log(colID);
                 dataParse = data[colTitle];
                 //console.log(dataParse);
                 var cajas = dataParse[i] == false? "":JSON.parse(dataParse[i]);
                 var cajaKeys = Object.keys(cajas)
                 var arraySection = [];
                 for (let index = 0; index < cajaKeys.length; index++) {
                  let titleArray = cajaKeys[index];
                  let jsonString = JSON.stringify(cajas[cajaKeys[index]])
                   jsonString= jsonString.replace("{","")
                   jsonString= jsonString.split('"').join(' ');
                   jsonString= jsonString.replace("}"," ")
                   jsonString= jsonString.split("null").join('N/A ');
                   jsonString= jsonString.split("vacio").join('N/A ');
                   arraySection[titleArray] = jsonString;
                  columns_A = {...arraySection}
                };
                 let ObjectID_altura = {ID: colID[i],...columns_A};
                 altura.push(ObjectID_altura)
                 break;
             }
            }
        }
        
    $(document).ready(function() {
      let exportar = document.createElement('button');
      exportar.id = "exportar";
      exportar.innerHTML = "Exportar a Excel <i class='far fa-file-excel'></i> ";
      exportar.classList = ('btn', 'btn-secondary', 'buttons-excel', 'buttons-html5', 'btn-success');
      exportar.onclick = function(){
        exportarExcel();
      };
      document.getElementById("descarga").appendChild(exportar);
      function exportarExcel(){
      //console.log(vision)  
               // get table
    var table = document.getElementById("descarga");
    var table2 = torque;
    var table3 = intentos_t;
     var table4 = intentos_va;
     var table5 = vision;
     var table6 = altura;
     var table7 = angulo;
    // convert table to excel sheet
    var wb = XLSX.utils.table_to_book(table, {sheet:"Historial"});
    wb["Sheets"]["Historial"]["!cols"] = 
    [{wpx : 50 },{ wpx : 126 },{ wpx : 126 },
    { wpx : 86 },{ wpx : 88 },{ wpx : 90 },
    { wpx : 110 },{ wpx : 190 },{ wpx : 250 },{ wpx : 250 }];
    //var fila1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];
    /*for (let columna = 0; columna < fila1.length; columna++) {
      const celda = fila1[columna];
      ws[`${celda}1`].s = {
        font: {
          name: "Arial",
          sz: 18,
          bold: true,
          color: { rgb: "111" },
        },
        fill: {
          bgColor: {rgb: "FFFF6550"}
        }
      };
   
    }*/
    
    wb.SheetNames.push("Torque");
    var ws2 = XLSX.utils.json_to_sheet(table2, {sheet:"Torque"});
    wb.Sheets["Torque"] = ws2;
    //wb["Sheets"]["Torque"]["!cols"] = 
    // [{wpx : 60 },{ wpx : 80 },{ wpx : 80 },
    // { wpx : 80 },{ wpx : 90 },{ wpx : 300 },
    // { wpx : 300 },{ wpx : 190 },{ wpx : 300 }];
    //var fila1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];
    wb.SheetNames.push("Intentos-t");
    var ws3 = XLSX.utils.json_to_sheet(table3, {sheet:"Intentos-t"});
    wb.Sheets["Intentos-t"] = ws3;

    wb.SheetNames.push("Intentos-va");
    var ws4 = XLSX.utils.json_to_sheet(table4, {sheet:"Intentos-va"});
    wb.Sheets["Intentos-va"] = ws4;

    wb.SheetNames.push("Vision");
    var ws5 = XLSX.utils.json_to_sheet(table5, {sheet:"Vision"});
    wb.Sheets["Vision"] = ws5;

    wb.SheetNames.push("Altura");
    var ws6 = XLSX.utils.json_to_sheet(table6, {sheet:"Altura"});
    wb.Sheets["Altura"] = ws6;

    wb.SheetNames.push("Angulo");
    var ws7 = XLSX.utils.json_to_sheet(table7, {sheet:"Angulo"});
    wb.Sheets["Angulo"] = ws7;

    // wb.SheetNames.push("Intentos-t");
    // var ws3 = XLSX.utils.json_to_sheet(table3, {sheet:"Intentos-t"});
    // wb.Sheets["Intentos-t"] = ws3;
    // wb["Sheets"]["Intentos-t"]["!cols"] = 
    // [{wpx : 85 },{ wpx : 85 },{ wpx : 85 },
    // { wpx : 85 },{ wpx : 85 },{ wpx : 350 },
    // { wpx : 310 },{ wpx : 140 },{ wpx : 573 },];
    
    // write sheet to blob
    var blob = new Blob([s2ab(XLSX.write(wb, {bookType:'xlsx', type:'binary'}))], {
	    type: "application/octet-stream"
	});
    // return sheet file
    return saveAs(blob, "Fujikura Automotive México Piedras Negras.xlsx");
      };
      function s2ab(s) {
        var buf = new ArrayBuffer(s.length);
        var view = new Uint8Array(buf);
        for (var i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
        return buf;
    }



     /* $('#myTable_descarga').DataTable({
        dom: 'B',
          buttons: [
          {
            extend: 'excelHtml5',
            text: 'Exportar a Excel <i class="fas fa-file-excel"></i>',
            titleAttr: 'Exportar a Excel',
            className: 'btn btn-success',
            title: "Fujikura Automotive México Piedras Negras",
            messageTop: "Información recopilada por las estaciones de Torque y Visión",
            excelStyles:[{
              template: "cyan_medium",
            },
            {
              cells: 'sD',
              condition:{
                type: 'cellIs',
                operator: 'equal',
                formula: 2
              },
              style:{
                font:{
                  b:true
                },
                fill:{
                  pattern:{
                    bgColor: '05BA47'
                  }
                }
              }
            }
          ]
          }
          ]
      });*/
    } );
    setTimeout( () => {
      resovle('Las Tablas estan listas para ser descargadas');
     },1000);
  });
}

$(document).on('click','.btn-ver-vision', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
   
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      let re = /null/g;
      let visionValue = data[id_info].replace(re, 'N/A');
      // console.log(visionValue);
      document.getElementById("informacion").innerHTML = visionValue;
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      let re = /null/g;
      dataParse = JSON.parse(data[header_info]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
  
});
$(document).on('click','.btn-ver-altura', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      let re = /null/g;
      let alturaValue = data[id_info].replace(re, 'N/A');
      // console.log(alturaValue);
      //document.getElementById("informacion").innerHTML = alturaValue;
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      let re = /null/g;
      dataParse = JSON.parse(data[header_info]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)

      //let alturaValue = data[header_info].replace(re, 'N/A');
      // console.log(alturaValue);
      //document.getElementById("informacion").innerHTML = alturaValue;
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-intentosva', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      console.log(headerString)
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse;
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length -1; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');
          // let numList = Number(obj_cavidad);
          
          //   numList = Number(obj_cavidad)+ 1;
          
          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      
      }
      document.getElementById("informacion").appendChild(div)

      //let alturaValue = data[header_info].replace(re, 'N/A');
      // console.log(alturaValue);
      //document.getElementById("informacion").innerHTML = alturaValue;
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-torque', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      let re = /null/g;
      let valueCav = data[id_info].replace(re, 'N/A');
      // console.log(valueCav);
      document.getElementById("informacion").innerHTML = valueCav;
      $('#mostrar').click();
    })  
  } else{
    //console.log("ID del registro: ",id_info);
    //console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      // console.log(data);
      // console.log(data[header_info]);
      let re = /null/g;
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');
          let unidadMedida = boxValue === 'N/A'?  '' :'Nm';
          span.innerHTML = `<p>${obj_cavidad}: ${boxValue} ${unidadMedida}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-angulo', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      let re = /null/g;
      let angleValue = data[id_info].replace(re, 'N/A');
      // console.log(angleValue);
      document.getElementById("informacion").innerHTML = angleValue;
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      if (data[header_info] == ""){
        document.getElementById("informacion").appendChild(document.createTextNode("N/A"));
      }else{
        let re = /null/g;
        dataParse = JSON.parse(data[header_info]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)
      }
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-intentost', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      let re = /0/g;
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    let headerString = header_info.replace(/ /g,"_");
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      let re = /0/g;
      dataParse = JSON.parse(data[headerString]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-scrap', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      let re = /0/g;
      dataParse = JSON.parse(data[id_info]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      let re = /0/g;
      dataParse = JSON.parse(data[header_info]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-seriales', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
       // console.log(data);
      // console.log(data[header_info]);
      let re = /0/g;
      dataParse = JSON.parse(data[id_info]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

         //console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        // console.log("Aquí en object: ",cavidades)
        
         
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         
         let span = document.createElement("span");
         span.classlist = "caja-valor";
         span.innerHTML = `<p>${cavidades}</p>`;
         nav.appendChild(span);
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })  

  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/historial/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      let re = /0/g;
      dataParse = JSON.parse(data[header_info]);
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

         //console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        // console.log("Aquí en object: ",cavidades)
        
         
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         
         let span = document.createElement("span");
         span.classlist = "caja-valor";
         span.innerHTML = `<p>${cavidades}</p>`;
         nav.appendChild(span);
      }
     
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-operacion', function(){
 
  document.getElementById("informacion").innerHTML = "";
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  
  var id_info_responsive = header.parent().prev().find("td:first").text();
  //console.log(id_info);
  document.getElementById("header").innerHTML = id_info;
  let div = document.createElement("div");
  //div.classList = `flex-box justify-evenly`;
  if (isNaN(id_info)){
    fetch(dominio+"/api/get/historial/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{ 
     // console.log(id_info)//columna donde los valores entrarán
      console.log(id_info_responsive)//
      //console.log(data["FIN"]);
      /**OBTENIENDO LOS DATOS DEL ARCHIVO PARA IMPRIMIR**/
       let dataParse_serial = JSON.parse(data["SERIALES"]);
       
       var dateYear =new Date(data["INICIO"]).getUTCFullYear()
       var dateMonth = new Date(data["INICIO"]).getUTCMonth() + 1;
       var dateDay = new Date(data["INICIO"]).getUTCDate()
        var dateHour = new Date(data["INICIO"]).getUTCHours()
        var dateMinutes = new Date(data["INICIO"]).getUTCMinutes()
        var dateSeconds = new Date(data["INICIO"]).getUTCSeconds()
        dateHour = dateHour < 10? '0'+ dateHour:dateHour; 
        dateMonth = dateMonth < 10? '0'+ dateMonth:dateMonth; 
        dateDay = dateDay < 10? '0'+ dateDay:dateDay; 
        dateMinutes = dateMinutes < 10? '0'+ dateMinutes:dateMinutes; 
        dateSeconds = dateSeconds < 10? '0'+ dateSeconds:dateSeconds; 
      //console.log(dateYear)
      //console.log(dateMonth)
      var dateStamp = dateYear+"/"+dateMonth+"/"+dateDay+" "+dateHour+":"+dateMinutes+":"+dateSeconds
      console.log(dateStamp)

       let torque = JSON.parse(data["TORQUE"]);
       // console.log("Convertido a JSON_serial",dataParse_serial);
       // console.log("Convertido a JSON_torque",torque);
       var hm = dataParse_serial["HM"];
       //console.log(hm);
       var ref = dataParse_serial["REF"];
       //console.log(ref);
      /**CREANDO LA ESTRUCTURA DEL FORMATO**/

       var hmText = document.createElement("input");
       hmText.id = "hmText";
       var hmBox = document.createElement("span");

       var refText = document.createElement("input");
       refText.id = "refText";
       var refBox = document.createElement("span");
       var finText = document.createElement("input");
       finText.id = "finText";
       var finBox = document.createElement("span");

       var torText = document.createElement("input");
       torText.id = "torValue";
       var torBox = document.createElement("span");


       
       //hmBox.classList = "text-center";
       hmBox.innerHTML = `<b>HM</b>`
       hmText.setAttribute("type", "text");
       hmText.setAttribute("value", hm); // Valor de HM
       hmBox.appendChild(hmText)
       div.appendChild(hmBox);
       
       //refBox.classList = "text-center";
       refBox.innerHTML = `<b>REFERENCIA</b>`
       refText.setAttribute("type", "text");
       refText.setAttribute("value", ref); // Valor de ref
       refBox.appendChild(refText);
       div.appendChild(refBox);
       
       //finBox.classList = "text-center";
       finBox.innerHTML = `<b>FECHA</b>`
       finText.setAttribute("type", "text");
       finText.setAttribute("value", dateStamp); //Valor de fecha Final
       finBox.appendChild(finText)
       div.appendChild(finBox);

      if (sessionStorage.getItem('tipo') === "SUPERUSUARIO" || sessionStorage.getItem('tipo') === "CALIDAD"){
       torBox.innerHTML = `<b>TORQUE</b>`
       torText.setAttribute("type", "text");
       torText.setAttribute("value", JSON.stringify(torque)); //Valor de fecha toral
       torBox.appendChild(torText)
       div.appendChild(torBox);
      }
      else{
       document.getElementById("refText").disabled = true
       document.getElementById("hmText").disabled = true
       document.getElementById("finText").disabled = true

        torBox.innerHTML = `<b>TORQUE</b>`
       torText.setAttribute("type", "text");
       torText.setAttribute("value", JSON.stringify(torque)); //Valor de fecha toral
       torBox.appendChild(torText)
       torBox.style.display = "none";
       div.appendChild(torBox);
      }
      /** Boton Imprimir **/ 
      let printButton = document.createElement('button');
      printButton.innerHTML = "Imprimir";
      printButton.classList =  "btn-print";
      printButton.onclick = function(){
        imprimir(); //envios de los datos al POST
      };
      div.appendChild(printButton);      
    });
  }
 
  document.getElementById("informacion").appendChild(div)

  $('#mostrar').click();
});
/*
HM, DATE, REF, TORQUES
*/
function imprimir(){
 var formData = new FormData();
 hmText = document.getElementById("hmText").value
 refText = document.getElementById("refText").value
 finText = document.getElementById("finText").value
 torText = document.getElementById("torValue").value
 
 formData.set('HM',hmText)
 formData.set('REF',refText)
 formData.set('DATE',finText)
 formData.set('TORQUES',torText)
 console.log(`ENVIANDO.. HM: ${hmText} || REF: ${refText} || Fecha Final: ${finText} || TORQUES: ${torText}`);    

  fetch(dominio+'/printer/etiqueta',{ //Envio de datos para impr
    method: 'POST',
    body: formData
}).then(res=>res.json())
.then(function (data){
    console.log(data);
    console.log('Impresion exitosa');
    console.log(`HM: ${hmText} || REF: ${refText} || Fecha Final: ${finText} || TORQUES: ${torText}`);    
})
.catch(function(err) {
    console.log(err);
});
}

//////////////// AL SELECCIONAR TABLAS QUE NECESITEN REALIZAR CONSULTAS EN BASE AL "ID" SE EJECUTARÁ ESTA FUNCIÓN ////////////////////////
function cargarmodulo(){
  var moduloinput = document.getElementById("moduloinput").value;
  if ($('#tipo_busqueda').val() == "Modulo") {
    // console.log("URL POR MODULO");
    var url = dominio+"/api/get/"+document.getElementById('selector').value+"/modulo/=/"+moduloinput+"/_/=/_";
  }else{
    // console.log("URL POR ID");
    url = dominio+"/api/get/"+document.getElementById('selector').value+"/id/>/"+document.getElementById('idi').value+"/id/</"+document.getElementById('idf').value;
  }
  fetch(url)
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';    
      var colnames = Object.keys(data);
      console.log(colnames[colnames.indexOf("ID")]);
      colnames.splice(0,0, colnames[colnames.indexOf("ID")]);
      
      colnames.splice(colnames.indexOf("MODULO")-1,1);
      console.log("Colnames: ",colnames);
      var filas;
      if ($('#tipo_busqueda').val() == "Modulo") {
        filas = 1;
      }else{
        filas = data[colnames[0]].length;
      }
      // console.log("Resultado de Filas: ",filas);
      //CREACIÓN DE TABLA
      var myTableDiv = document.getElementById("resultado");
      var table = document.createElement('TABLE');
      var tableBody = document.createElement('TBODY');
      var Encabezados = document.createElement('THEAD');

      table.id = "myTable";
      table.classList.add('display');
      table.classList.add('nowrap');
      table.cellSpacing="0";
      table.width="100%";
      table.border = '2';
      table.appendChild(Encabezados);
      table.appendChild(tableBody);
      tableBody.align="center";
      //FIN DE CREACIÓN DE TABLA

      //ENCABEZADOS DE LA TABLA
      var tr = document.createElement('TR');
      Encabezados.appendChild(tr);
      for (i = 0; i < colnames.length; i++) {
          var th = document.createElement('TH')
          var titulo = colnames[i].replace("_"," ")
          th.width = '100';
          console.log(colnames[i]);
          th.appendChild(document.createTextNode(titulo));
          tr.appendChild(th).style.backgroundColor="#0DBED6";
      }
      //FILAS DE LA TABLA
      for (i = 0; i < filas; i++) {
        var tr = document.createElement('TR');
        for (j = 0; j < colnames.length; j++) {
          var td = document.createElement('TD')
          switch (colnames[j]){
          case "CAJA_1":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja1');
            }else{
              boton.classList.add('btn-ver-caja1_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_2":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja2');
            }else{
              boton.classList.add('btn-ver-caja2_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_3":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja3');
            }else{
              boton.classList.add('btn-ver-caja3_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_4":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja4');
            }else{
              boton.classList.add('btn-ver-caja4_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_5":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja5');
            }else{
              boton.classList.add('btn-ver-caja5_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_6":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja6');
            }else{
              boton.classList.add('btn-ver-caja6_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_7":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja7');
            }else{
              boton.classList.add('btn-ver-caja7_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_8":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja8');
            }else{
              boton.classList.add('btn-ver-caja8_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          case "CAJA_9":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            if (document.getElementById('selector').value == "Modulos_Fusibles") {
              boton.classList.add('btn-ver-caja9');
            }else{
              boton.classList.add('btn-ver-caja9_1');
            }
            boton.style.width="60px";
            boton.appendChild(icono);
            td.appendChild(boton);
            break;
          default:
            if ($('#tipo_busqueda').val() == "Modulo") {
              td.appendChild(document.createTextNode(data[colnames[j]]));
            }else{
              td.appendChild(document.createTextNode(data[colnames[j]][i]));
            }
            
          break;
        }
          tr.appendChild(td)
        }
        tableBody.appendChild(tr);
      }
      myTableDiv.appendChild(table);
      $(document).ready(function() {
          $('#myTable').DataTable({
            responsive:true
          });
      } );
    }
  })
}

$(document).on('click','.btn-ver-caja1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja2', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja3', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja4', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja5', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja6', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja7', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja8', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
       let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});

$(document).on('click','.btn-ver-caja1_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_1");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_1";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_1"]);
      document.getElementById("informacion").innerHTML = data["CAJA_1"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja2_1', function(){
  
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA 2");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA 2";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_2"]);
      document.getElementById("informacion").innerHTML = data["CAJA_2"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja3_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_3");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_3";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_3"]);
      document.getElementById("informacion").innerHTML = data["CAJA_3"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja4_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_4");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_4";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_4"]);
      document.getElementById("informacion").innerHTML = data["CAJA_4"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja5_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_5");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_5";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_5"]);
      document.getElementById("informacion").innerHTML = data["CAJA_5"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja6_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_6");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_6";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_6"]);
      document.getElementById("informacion").innerHTML = data["CAJA_6"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja7_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_7");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_7";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_7"]);
      document.getElementById("informacion").innerHTML = data["CAJA_7"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja8_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_8");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_8";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_8"]);
      document.getElementById("informacion").innerHTML = data["CAJA_8"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
$(document).on('click','.btn-ver-caja9_1', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ","CAJA_9");
    var id_info_responsive = header.parent().prev().find("td:first").next().next().next().next().next().next().next().next().next().text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "CAJA_9";
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      console.log(data);
      console.log(data["CAJA_9"]);
      document.getElementById("informacion").innerHTML = data["CAJA_9"];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');

          span.innerHTML = `<p>${obj_cavidad}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
        }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});
function cargarnombre(){
  var nombreinput = document.getElementById("nombreinput").value;
  // console.log(nombreinput);
  fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/name/=/"+nombreinput+"/_/=/_")
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';
    }

    var colnames = Object.keys(data);
    // console.log("Colnames: ",colnames);
    colnames.splice(colnames.indexOf("GAFET"),1);
    // console.log("el nuevo array: ", colnames);
    var filas = data[colnames[0]].length;
    // console.log("Resultado: ",filas);
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.classList.add('nowrap');
    table.cellSpacing="0";
    table.width="100%";
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
      th.width = '100';
      th.appendChild(document.createTextNode(colnames[i]));
      tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        td.appendChild(document.createTextNode(data[colnames[j]][i]));
        tr.appendChild(td)
      }
      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable({
        responsive:true
      });
    } );
  })
}

function cargarnombresuper(){
  var nombreinput = document.getElementById("nombreinput").value;
  // console.log(nombreinput);
  fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/name/=/"+nombreinput+"/_/=/_")
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';
    }

    var colnames = Object.keys(data);
    // console.log("Colnames: ",colnames);
    var filas = data[colnames[0]].length;
    // console.log("Resultado: ",filas);
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
      th.width = '100';
      th.appendChild(document.createTextNode(colnames[i]));
      tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        td.appendChild(document.createTextNode(data[colnames[j]][i]));
        tr.appendChild(td)
      }
      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable();
    } );
  })
}

function cargargafete(){
  var gafeteinput = document.getElementById("gafeteinput").value;
  // console.log(gafeteinput);
  fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/gafet/=/"+gafeteinput+"/_/=/_")
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';
    }

    var colnames = Object.keys(data);
    // console.log("Colnames: ",colnames);
    colnames.splice(colnames.indexOf("GAFET"),1);
    // console.log("el nuevo array: ", colnames);
    var filas = data[colnames[0]].length;
    // console.log("Resultado: ",filas);
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.classList.add('nowrap');
    table.cellSpacing="0";
    table.width="100%";
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
      th.width = '100';
      th.appendChild(document.createTextNode(colnames[i]));
      tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        td.appendChild(document.createTextNode(data[colnames[j]][i]));
        tr.appendChild(td)
      }
      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable({
        responsive:true
      });
    } );
  })
}

function cargargafetesuper(){
  var gafeteinput = document.getElementById("gafeteinput").value;
  // console.log(gafeteinput);
  fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/gafet/=/"+gafeteinput+"/_/=/_")
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';
    }

    var colnames = Object.keys(data);
    // console.log("Colnames: ",colnames);
    var filas = data[colnames[0]].length;
    // console.log("Resultado: ",filas);
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
      th.width = '100';
      th.appendChild(document.createTextNode(colnames[i]));
      tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < filas; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        td.appendChild(document.createTextNode(data[colnames[j]][i]));
        tr.appendChild(td)
      }
      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable();
    } );
  })
}

function cargarnombre_usuarios(){
  var nombreinput = document.getElementById("nombreinput").value;
  // console.log(nombreinput);
  fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/name/=/"+nombreinput+"/_/=/_")
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';    
      var colnames = Object.keys(data);
      // console.log("Colnames: ",colnames);
      colnames.splice(colnames.indexOf("GAFET"),1);
      // console.log("el nuevo array: ", colnames);
      var filas = data[colnames[0]];
      // console.log("Resultado: ",filas);
      //CREACIÓN DE TABLA
      var myTableDiv = document.getElementById("resultado");
      var table = document.createElement('TABLE');
      var tableBody = document.createElement('TBODY');
      var Encabezados = document.createElement('THEAD');

      table.id = "myTable";
      table.classList.add('display');
      table.classList.add('nowrap');
      table.cellSpacing="0";
      table.width="100%";
      table.border = '2';
      table.appendChild(Encabezados);
      table.appendChild(tableBody);
      tableBody.align="center";
      //FIN DE CREACIÓN DE TABLA

      //ENCABEZADOS DE LA TABLA
      var tr = document.createElement('TR');
      Encabezados.appendChild(tr);
      for (i = 0; i < colnames.length; i++) {
        var th = document.createElement('TH')
        th.width = '100';
        th.appendChild(document.createTextNode(colnames[i]));
        tr.appendChild(th).style.backgroundColor="#0DBED6";
      }
      //FILAS DE LA TABLA
      for (i = 0; i < 1; i++) {
        var tr = document.createElement('TR');
        for (j = 0; j < colnames.length; j++) {
          var td = document.createElement('TD')
          td.appendChild(document.createTextNode(data[colnames[j]]));
          tr.appendChild(td)
        }
        tableBody.appendChild(tr);
      }
      myTableDiv.appendChild(table);
      $(document).ready(function() {
        $('#myTable').DataTable({
          responsive:true
        });
      } );
    }
  })
}

function cargargafete_usuarios(){
  var gafeteinput = document.getElementById("gafeteinput").value;
  // console.log(gafeteinput);
  fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/gafet/=/"+gafeteinput+"/_/=/_")
  .then(data=>data.json())
  .then(data=>{
    // console.log(data);
    if (data.items == 0) {
      console.log("No hay coincidencias");
      alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
    }else{
      alertawarning.innerHTML = '';    
      var colnames = Object.keys(data);
      // console.log("Colnames: ",colnames);
      colnames.splice(colnames.indexOf("GAFET"),1);
      // console.log("el nuevo array: ", colnames);
      var filas = data[colnames[0]];
      // console.log("Resultado: ",filas);
      //CREACIÓN DE TABLA
      var myTableDiv = document.getElementById("resultado");
      var table = document.createElement('TABLE');
      var tableBody = document.createElement('TBODY');
      var Encabezados = document.createElement('THEAD');

      table.id = "myTable";
      table.classList.add('display');
      table.classList.add('nowrap');
      table.cellSpacing="0";
      table.width="100%";
      table.border = '2';
      table.appendChild(Encabezados);
      table.appendChild(tableBody);
      tableBody.align="center";
      //FIN DE CREACIÓN DE TABLA

      //ENCABEZADOS DE LA TABLA
      var tr = document.createElement('TR');
      Encabezados.appendChild(tr);
      for (i = 0; i < colnames.length; i++) {
        var th = document.createElement('TH')
        th.width = '100';
        th.appendChild(document.createTextNode(colnames[i]));
        tr.appendChild(th).style.backgroundColor="#0DBED6";
      }
      //FILAS DE LA TABLA
      for (i = 0; i < 1; i++) {
        var tr = document.createElement('TR');
        for (j = 0; j < colnames.length; j++) {
          var td = document.createElement('TD')
          td.appendChild(document.createTextNode(data[colnames[j]]));
          tr.appendChild(td)
        }
        tableBody.appendChild(tr);
      }
      myTableDiv.appendChild(table);
      $(document).ready(function() {
        $('#myTable').DataTable({
          responsive:true
        });
      } );
    }
  })
}

function cargarpedido(){
  console.log("FUNCION PEDIDOS ACTIVADA")
  switch ($('#tipo_busqueda').val()){
    case "Fecha":
    cargardatetime();
    break;
    case "Pedido":
    var pedidoinput = document.getElementById("pedidoinput").value;
    // console.log(pedidoinput);
    fetch(dominio+"/api/get/"+document.getElementById('selector').value+"/pedido/=/"+pedidoinput+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      if (data.items == 0) {
        console.log("No hay coincidencias");
        alertawarning.innerHTML = '<div class="alert alert-warning" role="alert">No existen coincidencias en la base de datos.</div>';
      }else{
        alertawarning.innerHTML = '';
      }

      var colnames = Object.keys(data);
      console.log(colnames);
      colnames.splice(colnames.indexOf("ID"),1);
      colnames.splice(colnames.indexOf("PEDIDO"),1,"ACTIVE");
      colnames.splice(colnames.indexOf("ACTIVE"),1,"ID","PEDIDO");
      // console.log("Colnames: ",colnames);
      var filas = data[colnames[0]];
      // console.log("Resultado: ",filas);
    //CREACIÓN DE TABLA
    var myTableDiv = document.getElementById("resultado");
    var table = document.createElement('TABLE');
    var tableBody = document.createElement('TBODY');
    var Encabezados = document.createElement('THEAD');

    table.id = "myTable";
    table.classList.add('display');
    table.classList.add('nowrap');
    table.cellSpacing="0";
    table.width="100%";
    table.border = '2';
    table.appendChild(Encabezados);
    table.appendChild(tableBody);
    tableBody.align="center";
    //FIN DE CREACIÓN DE TABLA

    //ENCABEZADOS DE LA TABLA
    var tr = document.createElement('TR');
    Encabezados.appendChild(tr);
    
    for (i = 0; i < colnames.length; i++) {
      var th = document.createElement('TH')
          var titulo = colnames[i].replace("_"," ")
          th.width = '100';
          console.log(colnames[i]);
          th.appendChild(document.createTextNode(titulo));
          tr.appendChild(th).style.backgroundColor="#0DBED6";
    }
    //FILAS DE LA TABLA
    for (i = 0; i < 1; i++) {
      var tr = document.createElement('TR');
      for (j = 0; j < colnames.length; j++) {
        var td = document.createElement('TD')
        switch (colnames[j]) {
          case "QR_BOXES":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-qrcode");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-qr2');
            boton.style.width="60px"
            boton.appendChild(icono);
            td.appendChild(boton);
          break;
          case "MODULOS_VISION":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-modulosF');
            boton.style.width="60px"
            boton.appendChild(icono);
            td.appendChild(boton);
          break;
          case "MODULOS_ALTURA":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-modulosA');
            boton.style.width="60px"
            boton.appendChild(icono);
            td.appendChild(boton);
          break;
          case "MODULOS_TORQUE":
            var boton = document.createElement('button');
            var icono = document.createElement('i');
            icono.classList.add("fas");
            icono.classList.add("fa-archive");
            boton.title = "Ver Información";
            boton.classList.add('btn');
            boton.classList.add('btn-info');
            boton.classList.add('btn-ver-modulosT');
            boton.style.width="60px"
            boton.appendChild(icono);
            td.appendChild(boton);
          break;
          default:
            td.appendChild(document.createTextNode(data[colnames[j]]));
        }
        tr.appendChild(td)
      }
      tableBody.appendChild(tr);
    }
    myTableDiv.appendChild(table);
    $(document).ready(function() {
      $('#myTable').DataTable({
        responsive:true
      });
    } );
  })
    break;
  }
}

$(document).on('click','.btn-ver-qr2', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true){
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = "QR_BOXES";
    fetch(dominio+"/api/get/pedidos/id/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data.QR_BOXES);
      document.getElementById("informacion").innerHTML = data.QR_BOXES;
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/pedidos/id/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
 
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
        let nav = document.createElement("nav");
        let caja = dataKeys[i];
        nav.id = "titulo-caja"
        nav.innerHTML = "<b>"+caja+"</b>";
        div.appendChild(nav);

        //console.log("Aqui esta la CAJA:",caja);
        let cavidades = dataParse[caja];
       // console.log("Aquí en object: ",cavidades)
       
        
        
        let grid = document.createElement("div");
        grid.classList = "grid-box";
        nav.appendChild(grid);
        
        let span = document.createElement("span");
        span.classlist = "caja-valor";
        span.innerHTML = `<p>${cavidades}</p>`;
        nav.appendChild(span);
     }
      document.getElementById("informacion").appendChild(div)
      $('#mostrar').click();
    })
  }
});

$(document).on('click','.btn-ver-modulosF', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/Pedidos/ID/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/Pedidos/ID/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box-1fr";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length -1; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');
          let numList = Number(obj_cavidad);
          
            numList = Number(obj_cavidad)+ 1;
          
          span.innerHTML = `<p>${numList}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      
      }
      document.getElementById("informacion").appendChild(div)

      //let alturaValue = data[header_info].replace(re, 'N/A');
      // console.log(alturaValue);
      //document.getElementById("informacion").innerHTML = alturaValue;
      $('#mostrar').click();
    })
  }
});

$(document).on('click','.btn-ver-modulosA', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/Pedidos/ID/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/Pedidos/ID/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box-1fr";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length -1; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');
          let numList = Number(obj_cavidad);
          
            numList = Number(obj_cavidad)+ 1;
          
          span.innerHTML = `<p>${numList}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      
      }
      document.getElementById("informacion").appendChild(div)

      //let alturaValue = data[header_info].replace(re, 'N/A');
      // console.log(alturaValue);
      //document.getElementById("informacion").innerHTML = alturaValue;
      $('#mostrar').click();
    })
  }
});

$(document).on('click','.btn-ver-modulosT', function(){
  var id_info = $(this).parent().parent().children().first().text();
  var header = $(this).closest("td");
  var header_info = header.closest( "table" ).find( "thead > tr > th" ).eq( header.index() ).text();
  if (isNaN(id_info)==true) {
    // console.log("CAMPO EN MODO RESPONSIVE");
    console.log("Header Responsive: ",id_info);
    var id_info_responsive = header.parent().prev().find("td:first").text();
    console.log("ID Responsive del registro: ",id_info_responsive);
    document.getElementById("header").innerHTML = id_info;
    fetch(dominio+"/api/get/Pedidos/ID/=/"+id_info_responsive+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      // console.log(data);
      // console.log(data[id_info]);
      document.getElementById("informacion").innerHTML = data[id_info];
      $('#mostrar').click();
    })  
  } else{
    console.log("ID del registro: ",id_info);
    console.log("Header: ",header_info);
    document.getElementById("header").innerHTML = header_info;
    fetch(dominio+"/api/get/Pedidos/ID/=/"+id_info+"/_/=/_")
    .then(data=>data.json())
    .then(data=>{
      document.getElementById("informacion").innerHTML = "";
      // console.log(data);
      // console.log(data[header_info]);
      document.getElementById("informacion").innerHTML = "";
      let headerString = header_info.replace(/ /g,"_");
      dataParse = JSON.parse(data[headerString]);
      let re = /null/g;
      // console.log("Convertido a JSON: ",dataParse)
      dataKeys = Object.keys(dataParse)
      // console.log("dataKeys: ",dataKeys)
      let div = document.createElement("div");
      for (let i = 0; i < dataKeys.length; i++) {
         let nav = document.createElement("nav");
         let caja = dataKeys[i];
         nav.id = "titulo-caja"
         nav.innerHTML = "<b>"+caja+"</b>";
         div.appendChild(nav);

        // console.log("Aqui esta la CAJA:",caja);
         let cavidades = dataParse[caja];
        //console.log("Aquí en object: ",cavidades)
        
         let get_cavidad = Object.getOwnPropertyNames(cavidades);
         
         let grid = document.createElement("div");
         grid.classList = "grid-box-1fr";
         nav.appendChild(grid);
         for (let j = 0; j < get_cavidad.length -1; j++) {

          let obj_cavidad = get_cavidad[j];
          //console.log ("cavidad",obj_cavidad);
          //console.log ("valor",cavidades[obj_cavidad]);
          let span = document.createElement("span");
          span.classlist = "caja-valor";
          let valores = JSON.stringify(cavidades[obj_cavidad]);
          //console.log("Aqui en string: ",valores)
          let boxValue = valores.replace(re, 'N/A');
          let numList = Number(obj_cavidad);
          
            numList = Number(obj_cavidad)+ 1;
          
          span.innerHTML = `<p>${numList}: ${boxValue}</p>`;
          grid.appendChild(span);
         }
      
      }
      document.getElementById("informacion").appendChild(div)

      //let alturaValue = data[header_info].replace(re, 'N/A');
      // console.log(alturaValue);
      //document.getElementById("informacion").innerHTML = alturaValue;
      $('#mostrar').click();
    })
  }
});

function cargarportipo(){
  // console.log("Este es el tipo que seleccionó: ",$('#tipo_busqueda').val());
  switch ($('#tipo_busqueda').val()){
    case "Fecha":
    // console.log("mostrando resultados por fecha");
    cargarfecha();
    break;
    case "Nombre":
    // console.log("mostrando resultados por nombre");
    cargarnombre();
    break;
    case "Gafet": //OJO AQUÍ, VERIFICAR SIEMPRE SI ES "GAFET" O "GAFETE" PARA EVITAR ERRORES
    // console.log("mostrando resultados por nombre");
    cargargafete();
    break;
  }
}

function cargarportipo_usuarios(){
  // console.log("Este es el tipo que seleccionó: ",document.getElementById("tipo").value);
  switch ($('#tipo_busqueda').val()){
    case "Fecha":
    // console.log("mostrando resultados porfecha");
    cargarfecha();
    break;
    case "Nombre":
    // console.log("mostrando resultados por nombre");
    cargarnombre_usuarios();
    break;
    case "Gafet":
    // console.log("mostrando resultados por nombre");
    cargargafete_usuarios();
    break;
  }
}
$('#modulo').on('keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) { 
    e.preventDefault();
    capturar();
  }
});

$('#pedido').on('keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) { 
    e.preventDefault();
    capturar();
  }
});

$('#nombre').on('keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) { 
    e.preventDefault();
    capturar();
  }
});

$('#gafete').on('keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) { 
    e.preventDefault();
    capturar();
  }
});

$('#HM').on('keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) { 
    e.preventDefault();
    capturar();
  }
});
document.addEventListener("DOMContentLoaded", () => {
    const contenedor = document.getElementById(
        "contenedor-agendamiento"
    );

    if (!contenedor) {
        return;
    }

    const formulario = document.getElementById(
        "formulario-agendamiento"
    );

    const pasos = Array.from(
        document.querySelectorAll(".paso-formulario")
    );

    const indicadores = Array.from(
        document.querySelectorAll(".indicador-paso")
    );

    const lineaProgreso = document.getElementById(
        "progreso-linea-activa"
    );

    const campoEspecialidad = document.getElementById(
        "id_especialidad"
    );

    const campoProfesional = document.getElementById(
        "id_profesional"
    );

    const campoServicio = document.getElementById(
        "id_servicio"
    );

    const campoFecha = document.getElementById(
        "id_fecha"
    );

    const campoHora = document.getElementById(
        "id_hora"
    );

    const listaEspecialidades = document.getElementById(
        "lista-especialidades"
    );

    const listaProfesionales = document.getElementById(
        "lista-profesionales"
    );

    const cargandoProfesionales = document.getElementById(
        "cargando-profesionales"
    );

    const textoEspecialidad = document.getElementById(
        "texto-especialidad-seleccionada"
    );

    const textoProfesional = document.getElementById(
        "texto-profesional-seleccionado"
    );

    const calendarioDias = document.getElementById(
        "calendario-dias"
    );

    const tituloMes = document.getElementById(
        "titulo-mes"
    );

    const botonMesAnterior = document.getElementById(
        "mes-anterior"
    );

    const botonMesSiguiente = document.getElementById(
        "mes-siguiente"
    );

    const listaHorarios = document.getElementById(
        "lista-horarios"
    );

    const cargandoHorarios = document.getElementById(
        "cargando-horarios"
    );

    const fechaHorarios = document.getElementById(
        "fecha-horarios"
    );

    const contenedorReferencia = document.getElementById(
        "contenedor-referencia"
    );

    const campoReferencia = document.getElementById(
        "id_referencia_pago"
    );

    const aceptarCondiciones = document.getElementById(
        "aceptar-condiciones"
    );

    const botonConfirmar = document.getElementById(
        "boton-confirmar"
    );

    const urlProfesionales =
        contenedor.dataset.urlProfesionales;

    const urlDisponibilidad =
        contenedor.dataset.urlDisponibilidad;

    const urlHorarios =
        contenedor.dataset.urlHorarios;

    const especialidadInicial =
        contenedor.dataset.especialidadInicial || "";

    const profesionalInicial =
        contenedor.dataset.profesionalInicial || "";

    const fechaInicial =
        contenedor.dataset.fechaInicial || "";

    const horaInicial =
        contenedor.dataset.horaInicial || "";

    const totalPasos = pasos.length;

    const hoy = new Date();

    hoy.setHours(0, 0, 0, 0);

    let pasoActual = 1;
    let pasoMaximoAlcanzado = 1;

    let mesVisible = new Date(
        hoy.getFullYear(),
        hoy.getMonth(),
        1
    );

    let especialidadSeleccionada = {
        id: "",
        nombre: "",
    };

    let profesionalSeleccionado = {
        id: "",
        nombre: "",
    };

    let servicioSeleccionado = {
        id: "",
        nombre: "",
        precio: "0.00",
        anticipo: "0.00",
        saldo: "0.00",
    };


    function escaparTexto(texto) {
        const elemento = document.createElement("div");

        elemento.textContent = texto || "";

        return elemento.innerHTML;
    }


    function fechaDesdeISO(fechaTexto) {
        if (!fechaTexto) {
            return null;
        }

        const partes = fechaTexto
            .split("-")
            .map(Number);

        if (
            partes.length !== 3
            || partes.some(Number.isNaN)
        ) {
            return null;
        }

        return new Date(
            partes[0],
            partes[1] - 1,
            partes[2]
        );
    }


    function formatearFecha(fechaTexto) {
        const fecha = fechaDesdeISO(fechaTexto);

        if (!fecha) {
            return "Sin seleccionar";
        }

        return new Intl.DateTimeFormat(
            "es-EC",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
            }
        ).format(fecha);
    }


    function formatearMes(fecha) {
        const texto = new Intl.DateTimeFormat(
            "es-EC",
            {
                month: "long",
                year: "numeric",
            }
        ).format(fecha);

        return (
            texto.charAt(0).toUpperCase()
            + texto.slice(1)
        );
    }


    function limpiarMensajesJavaScript() {
        document
            .querySelectorAll(".mensaje-validacion-js")
            .forEach((mensaje) => mensaje.remove());
    }


    function mostrarMensajePaso(
        numeroPaso,
        mensaje
    ) {
        limpiarMensajesJavaScript();

        const paso = document.querySelector(
            `[data-paso="${numeroPaso}"]`
        );

        if (!paso) {
            return;
        }

        const acciones = paso.querySelector(
            ".acciones-paso"
        );

        const alerta = document.createElement("div");

        alerta.className =
            "error-bloque mensaje-validacion-js";

        alerta.textContent = mensaje;

        if (acciones) {
            acciones.before(alerta);
        } else {
            paso.appendChild(alerta);
        }

        alerta.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    }


    function mostrarPaso(numeroPaso) {
        if (
            numeroPaso < 1
            || numeroPaso > totalPasos
        ) {
            return;
        }

        pasoActual = numeroPaso;

        pasoMaximoAlcanzado = Math.max(
            pasoMaximoAlcanzado,
            pasoActual
        );

        pasos.forEach((paso) => {
            const numero = Number(
                paso.dataset.paso
            );

            paso.classList.toggle(
                "activo",
                numero === pasoActual
            );
        });

        indicadores.forEach((indicador) => {
            const numero = Number(
                indicador.dataset.indicador
            );

            indicador.classList.toggle(
                "activo",
                numero === pasoActual
            );

            indicador.classList.toggle(
                "completado",
                numero < pasoActual
            );
        });

        const porcentaje = totalPasos > 1
            ? (
                (pasoActual - 1)
                / (totalPasos - 1)
            ) * 100
            : 0;

        lineaProgreso.style.width =
            `${porcentaje}%`;

        limpiarMensajesJavaScript();

        if (pasoActual === 5) {
            actualizarResumen();
        }

        contenedor.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    }


    function campoVacio(idCampo) {
        const campo = document.getElementById(
            idCampo
        );

        return (
            !campo
            || !String(campo.value).trim()
        );
    }


    function enfocarCampo(idCampo) {
        const campo = document.getElementById(
            idCampo
        );

        if (campo) {
            campo.focus();

            campo.reportValidity?.();
        }
    }


    function validarPasoUno() {
        const camposObligatorios = [
            ["id_nombres", "Ingresa los nombres completos."],
            ["id_apellidos", "Ingresa los apellidos completos."],
            ["id_nacionalidad", "Ingresa la nacionalidad."],
            [
                "id_tipo_documento",
                "Selecciona el tipo de documento.",
            ],
            [
                "id_cedula",
                "Ingresa el número de documento.",
            ],
            ["id_celular", "Ingresa el número celular."],
        ];

        for (const [
            idCampo,
            mensaje,
        ] of camposObligatorios) {
            if (campoVacio(idCampo)) {
                mostrarMensajePaso(1, mensaje);
                enfocarCampo(idCampo);

                return false;
            }
        }

        const correo = document.getElementById(
            "id_correo"
        );

        if (
            correo
            && correo.value
            && !correo.checkValidity()
        ) {
            mostrarMensajePaso(
                1,
                "Ingresa un correo electrónico válido."
            );

            correo.focus();
            correo.reportValidity();

            return false;
        }

        return true;
    }


    function validarPasoDos() {
        if (
            !campoEspecialidad
            || !campoEspecialidad.value
        ) {
            mostrarMensajePaso(
                2,
                "Selecciona una especialidad."
            );

            return false;
        }

        return true;
    }


    function validarPasoTres() {
        if (
            !campoProfesional
            || !campoProfesional.value
        ) {
            mostrarMensajePaso(
                3,
                "Selecciona un profesional."
            );

            return false;
        }

        return true;
    }


    function validarPasoCuatro() {
        if (!campoFecha || !campoFecha.value) {
            mostrarMensajePaso(
                4,
                "Selecciona una fecha disponible en verde."
            );

            return false;
        }

        if (!campoHora || !campoHora.value) {
            mostrarMensajePaso(
                4,
                "Selecciona uno de los horarios disponibles."
            );

            return false;
        }

        if (
            !campoServicio
            || !campoServicio.value
        ) {
            mostrarMensajePaso(
                4,
                "No se pudo identificar el servicio. Selecciona nuevamente la fecha."
            );

            return false;
        }

        return true;
    }


    function validarPasoCinco() {
        const metodoPago = formulario.querySelector(
            'input[name="metodo_pago"]:checked'
        );

        if (!metodoPago) {
            mostrarMensajePaso(
                5,
                "Selecciona un método de pago."
            );

            return false;
        }

        if (
            metodoPago.value === "TRANSFERENCIA"
            && (
                !campoReferencia
                || !campoReferencia.value.trim()
            )
        ) {
            mostrarMensajePaso(
                5,
                "Ingresa el número de comprobante o referencia."
            );

            campoReferencia?.focus();

            return false;
        }

        if (
            !aceptarCondiciones
            || !aceptarCondiciones.checked
        ) {
            mostrarMensajePaso(
                5,
                "Debes confirmar que los datos son correctos."
            );

            return false;
        }

        return true;
    }


    function validarPaso(numeroPaso) {
        switch (numeroPaso) {
            case 1:
                return validarPasoUno();

            case 2:
                return validarPasoDos();

            case 3:
                return validarPasoTres();

            case 4:
                return validarPasoCuatro();

            case 5:
                return validarPasoCinco();

            default:
                return true;
        }
    }


    document
        .querySelectorAll("[data-siguiente]")
        .forEach((boton) => {
            boton.addEventListener(
                "click",
                () => {
                    if (!validarPaso(pasoActual)) {
                        return;
                    }

                    mostrarPaso(pasoActual + 1);
                }
            );
        });


    document
        .querySelectorAll("[data-anterior]")
        .forEach((boton) => {
            boton.addEventListener(
                "click",
                () => {
                    mostrarPaso(pasoActual - 1);
                }
            );
        });


    indicadores.forEach((indicador) => {
        indicador.addEventListener(
            "click",
            () => {
                const destino = Number(
                    indicador.dataset.indicador
                );

                if (destino < pasoActual) {
                    mostrarPaso(destino);
                }
            }
        );
    });


    function limpiarProfesional() {
        profesionalSeleccionado = {
            id: "",
            nombre: "",
        };

        if (campoProfesional) {
            campoProfesional.value = "";
        }

        textoProfesional.textContent =
            "Selecciona un profesional para consultar su agenda.";

        limpiarAgenda();
    }


    function limpiarAgenda() {
        if (campoFecha) {
            campoFecha.value = "";
        }

        if (campoHora) {
            campoHora.value = "";
        }

        if (campoServicio) {
            campoServicio.value = "";
        }

        servicioSeleccionado = {
            id: "",
            nombre: "",
            precio: "0.00",
            anticipo: "0.00",
            saldo: "0.00",
        };

        calendarioDias.innerHTML = `
            <div class="estado-vacio calendario-vacio">
                <span>📆</span>
                <strong>Calendario pendiente</strong>
                <p>
                    Selecciona un profesional para
                    consultar su agenda.
                </p>
            </div>
        `;

        listaHorarios.innerHTML = `
            <div class="estado-vacio">
                <span>⏱️</span>
                <strong>Sin fecha seleccionada</strong>
                <p>
                    Los horarios disponibles
                    aparecerán aquí.
                </p>
            </div>
        `;

        fechaHorarios.textContent =
            "Selecciona una fecha verde.";

        actualizarResumen();
    }


    async function seleccionarEspecialidad(
        especialidadId,
        especialidadNombre,
        opciones = {}
    ) {
        especialidadSeleccionada = {
            id: String(especialidadId),
            nombre: especialidadNombre,
        };

        campoEspecialidad.value =
            String(especialidadId);

        document
            .querySelectorAll(".tarjeta-especialidad")
            .forEach((tarjeta) => {
                tarjeta.classList.toggle(
                    "seleccionada",
                    tarjeta.dataset.especialidadId
                    === String(especialidadId)
                );
            });

        textoEspecialidad.textContent =
            `Profesionales de ${especialidadNombre}`;

        limpiarProfesional();

        cargandoProfesionales.classList.remove(
            "oculto"
        );

        listaProfesionales.classList.add(
            "oculto"
        );

        try {
            const parametros = new URLSearchParams({
                especialidad_id:
                    String(especialidadId),
            });

            const respuesta = await fetch(
                `${urlProfesionales}?${parametros}`
            );

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error
                    || "No se pudieron cargar los profesionales."
                );
            }

            renderizarProfesionales(
                datos.profesionales
            );

            if (opciones.profesionalInicial) {
                const tarjetaProfesional =
                    listaProfesionales.querySelector(
                        `[data-profesional-id="${opciones.profesionalInicial}"]`
                    );

                if (tarjetaProfesional) {
                    await seleccionarProfesional(
                        opciones.profesionalInicial,
                        tarjetaProfesional.dataset
                            .profesionalNombre,
                        {
                            fechaInicial:
                                opciones.fechaInicial,
                            horaInicial:
                                opciones.horaInicial,
                        }
                    );
                }
            }
        } catch (error) {
            listaProfesionales.innerHTML = `
                <div class="estado-vacio">
                    <span>⚠️</span>
                    <strong>
                        No se pudieron cargar
                        los profesionales
                    </strong>
                    <p>${escaparTexto(error.message)}</p>
                </div>
            `;
        } finally {
            cargandoProfesionales.classList.add(
                "oculto"
            );

            listaProfesionales.classList.remove(
                "oculto"
            );
        }
    }


    function renderizarProfesionales(
        profesionales
    ) {
        listaProfesionales.innerHTML = "";

        if (!profesionales.length) {
            listaProfesionales.innerHTML = `
                <div class="estado-vacio">
                    <span>👥</span>
                    <strong>
                        No hay profesionales disponibles
                    </strong>
                    <p>
                        Esta especialidad todavía no
                        tiene profesionales activos.
                    </p>
                </div>
            `;

            return;
        }

        profesionales.forEach((profesional) => {
            const tarjeta = document.createElement(
                "button"
            );

            tarjeta.type = "button";

            tarjeta.className =
                "tarjeta-seleccion tarjeta-profesional";

            tarjeta.dataset.profesionalId =
                String(profesional.id);

            tarjeta.dataset.profesionalNombre =
                profesional.nombre;

            tarjeta.innerHTML = `
                <span class="avatar-profesional">
                    ${escaparTexto(profesional.iniciales)}
                </span>

                <span class="tarjeta-texto">
                    <strong>
                        ${escaparTexto(profesional.nombre)}
                    </strong>

                    <small>
                        ${escaparTexto(
                            profesional.especialidad
                        )}
                    </small>
                </span>

                <span class="marca-seleccion">
                    ✓
                </span>
            `;

            tarjeta.addEventListener(
                "click",
                () => seleccionarProfesional(
                    profesional.id,
                    profesional.nombre
                )
            );

            listaProfesionales.appendChild(
                tarjeta
            );
        });
    }


    async function seleccionarProfesional(
        profesionalId,
        profesionalNombre,
        opciones = {}
    ) {
        profesionalSeleccionado = {
            id: String(profesionalId),
            nombre: profesionalNombre,
        };

        campoProfesional.value =
            String(profesionalId);

        document
            .querySelectorAll(".tarjeta-profesional")
            .forEach((tarjeta) => {
                tarjeta.classList.toggle(
                    "seleccionada",
                    tarjeta.dataset.profesionalId
                    === String(profesionalId)
                );
            });

        textoProfesional.textContent =
            `Agenda de ${profesionalNombre}`;

        if (campoFecha) {
            campoFecha.value = "";
        }

        if (campoHora) {
            campoHora.value = "";
        }

        if (campoServicio) {
            campoServicio.value = "";
        }

        servicioSeleccionado = {
            id: "",
            nombre: "",
            precio: "0.00",
            anticipo: "0.00",
            saldo: "0.00",
        };

        const fechaRestaurada = fechaDesdeISO(
            opciones.fechaInicial
        );

        if (fechaRestaurada) {
            mesVisible = new Date(
                fechaRestaurada.getFullYear(),
                fechaRestaurada.getMonth(),
                1
            );
        } else {
            mesVisible = new Date(
                hoy.getFullYear(),
                hoy.getMonth(),
                1
            );
        }

        await cargarCalendario();

        if (opciones.fechaInicial) {
            await seleccionarFecha(
                opciones.fechaInicial,
                opciones.horaInicial || ""
            );
        }

        actualizarResumen();
    }


    listaEspecialidades?.addEventListener(
        "click",
        (evento) => {
            const tarjeta = evento.target.closest(
                ".tarjeta-especialidad"
            );

            if (!tarjeta) {
                return;
            }

            seleccionarEspecialidad(
                tarjeta.dataset.especialidadId,
                tarjeta.dataset.especialidadNombre
            );
        }
    );


    async function cargarCalendario() {
        if (!profesionalSeleccionado.id) {
            return;
        }

        tituloMes.textContent =
            formatearMes(mesVisible);

        calendarioDias.innerHTML = `
            <div class="estado-cargando calendario-vacio">
                <span class="cargador"></span>
                <p>Cargando disponibilidad...</p>
            </div>
        `;

        actualizarBotonMesAnterior();

        try {
            const parametros = new URLSearchParams({
                profesional_id:
                    profesionalSeleccionado.id,

                anio:
                    String(mesVisible.getFullYear()),

                mes:
                    String(mesVisible.getMonth() + 1),
            });

            const respuesta = await fetch(
                `${urlDisponibilidad}?${parametros}`
            );

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error
                    || "No se pudo cargar el calendario."
                );
            }

            renderizarCalendario(datos);
        } catch (error) {
            calendarioDias.innerHTML = `
                <div class="estado-vacio calendario-vacio">
                    <span>⚠️</span>
                    <strong>
                        No se pudo cargar el calendario
                    </strong>
                    <p>${escaparTexto(error.message)}</p>
                </div>
            `;
        }
    }


    function renderizarCalendario(datos) {
        calendarioDias.innerHTML = "";

        for (
            let indice = 0;
            indice < datos.primer_dia_semana;
            indice += 1
        ) {
            const espacio = document.createElement(
                "span"
            );

            espacio.className = "dia-vacio";

            calendarioDias.appendChild(espacio);
        }

        datos.dias.forEach((dia) => {
            const boton = document.createElement(
                "button"
            );

            boton.type = "button";

            boton.className =
                `dia-calendario ${dia.estado}`;

            boton.textContent = String(dia.dia);

            boton.dataset.fecha = dia.fecha;
            boton.dataset.estado = dia.estado;

            if (
                campoFecha.value
                && campoFecha.value === dia.fecha
            ) {
                boton.classList.add(
                    "seleccionada"
                );
            }

            if (dia.estado !== "disponible") {
                boton.disabled = true;

                boton.setAttribute(
                    "aria-disabled",
                    "true"
                );
            } else {
                boton.addEventListener(
                    "click",
                    () => seleccionarFecha(
                        dia.fecha
                    )
                );
            }

            calendarioDias.appendChild(boton);
        });
    }


    async function seleccionarFecha(
        fechaSeleccionada,
        horaRestaurada = ""
    ) {
        campoFecha.value = fechaSeleccionada;
        campoHora.value = "";

        document
            .querySelectorAll(".dia-calendario")
            .forEach((dia) => {
                dia.classList.toggle(
                    "seleccionada",
                    dia.dataset.fecha
                    === fechaSeleccionada
                );
            });

        fechaHorarios.textContent =
            formatearFecha(fechaSeleccionada);

        listaHorarios.classList.add("oculto");
        cargandoHorarios.classList.remove("oculto");

        try {
            const parametros = new URLSearchParams({
                profesional_id:
                    profesionalSeleccionado.id,

                fecha:
                    fechaSeleccionada,
            });

            const respuesta = await fetch(
                `${urlHorarios}?${parametros}`
            );

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error
                    || "No se pudieron cargar los horarios."
                );
            }

            servicioSeleccionado = {
                id: String(datos.servicio.id),
                nombre: datos.servicio.nombre,
                precio: datos.servicio.precio,
                anticipo: datos.servicio.anticipo,
                saldo: datos.servicio.saldo,
            };

            campoServicio.value =
                String(datos.servicio.id);

            renderizarHorarios(
                datos.horas,
                horaRestaurada
            );

            actualizarResumen();
        } catch (error) {
            listaHorarios.innerHTML = `
                <div class="estado-vacio">
                    <span>⚠️</span>
                    <strong>
                        No se pudieron cargar
                        los horarios
                    </strong>
                    <p>${escaparTexto(error.message)}</p>
                </div>
            `;
        } finally {
            cargandoHorarios.classList.add(
                "oculto"
            );

            listaHorarios.classList.remove(
                "oculto"
            );
        }
    }


    function renderizarHorarios(
        horarios,
        horaRestaurada = ""
    ) {
        listaHorarios.innerHTML = "";

        if (!horarios.length) {
            listaHorarios.innerHTML = `
                <div class="estado-vacio">
                    <span>🚫</span>
                    <strong>
                        No quedan horarios disponibles
                    </strong>
                    <p>
                        Selecciona otra fecha marcada
                        en verde.
                    </p>
                </div>
            `;

            return;
        }

        horarios.forEach((hora) => {
            const boton = document.createElement(
                "button"
            );

            boton.type = "button";
            boton.className = "boton-horario";
            boton.dataset.hora = hora;
            boton.textContent = hora;

            boton.addEventListener(
                "click",
                () => seleccionarHora(
                    hora,
                    boton
                )
            );

            listaHorarios.appendChild(boton);

            if (
                horaRestaurada
                && horaRestaurada.slice(0, 5)
                === hora.slice(0, 5)
            ) {
                seleccionarHora(hora, boton);
            }
        });
    }


    function seleccionarHora(
        hora,
        botonSeleccionado
    ) {
        campoHora.value = hora;

        document
            .querySelectorAll(".boton-horario")
            .forEach((boton) => {
                boton.classList.remove(
                    "seleccionado"
                );
            });

        botonSeleccionado.classList.add(
            "seleccionado"
        );

        actualizarResumen();
    }


    botonMesAnterior.addEventListener(
        "click",
        async () => {
            const mesAnterior = new Date(
                mesVisible.getFullYear(),
                mesVisible.getMonth() - 1,
                1
            );

            const mesActual = new Date(
                hoy.getFullYear(),
                hoy.getMonth(),
                1
            );

            if (mesAnterior < mesActual) {
                return;
            }

            mesVisible = mesAnterior;

            campoFecha.value = "";
            campoHora.value = "";

            await cargarCalendario();
        }
    );


    botonMesSiguiente.addEventListener(
        "click",
        async () => {
            mesVisible = new Date(
                mesVisible.getFullYear(),
                mesVisible.getMonth() + 1,
                1
            );

            campoFecha.value = "";
            campoHora.value = "";

            await cargarCalendario();
        }
    );


    function actualizarBotonMesAnterior() {
        const mesActual = new Date(
            hoy.getFullYear(),
            hoy.getMonth(),
            1
        );

        botonMesAnterior.disabled =
            mesVisible <= mesActual;
    }


    function actualizarResumen() {
        const nombres =
            document.getElementById("id_nombres")
                ?.value
                .trim() || "";

        const apellidos =
            document.getElementById("id_apellidos")
                ?.value
                .trim() || "";

        const usuario = (
            `${nombres} ${apellidos}`
        ).trim();

        document.getElementById(
            "resumen-usuario"
        ).textContent =
            usuario || "Sin información";

        document.getElementById(
            "resumen-especialidad"
        ).textContent =
            especialidadSeleccionada.nombre
            || "Sin seleccionar";

        document.getElementById(
            "resumen-profesional"
        ).textContent =
            profesionalSeleccionado.nombre
            || "Sin seleccionar";

        document.getElementById(
            "resumen-fecha"
        ).textContent =
            campoFecha.value
            ? formatearFecha(campoFecha.value)
            : "Sin seleccionar";

        document.getElementById(
            "resumen-hora"
        ).textContent =
            campoHora.value
            ? campoHora.value.slice(0, 5)
            : "Sin seleccionar";

        document.getElementById(
            "resumen-precio"
        ).textContent =
            servicioSeleccionado.precio;

        document.getElementById(
            "resumen-anticipo"
        ).textContent =
            servicioSeleccionado.anticipo;

        document.getElementById(
            "resumen-saldo"
        ).textContent =
            servicioSeleccionado.saldo;
    }


    formulario
        .querySelectorAll(
            'input[name="metodo_pago"]'
        )
        .forEach((radio) => {
            radio.addEventListener(
                "change",
                actualizarMetodoPago
            );
        });


    function actualizarMetodoPago() {
        const seleccionado =
            formulario.querySelector(
                'input[name="metodo_pago"]:checked'
            );

        const esTransferencia =
            seleccionado?.value === "TRANSFERENCIA";

        contenedorReferencia.classList.toggle(
            "oculto",
            !esTransferencia
        );

        if (!esTransferencia && campoReferencia) {
            campoReferencia.value = "";
        }
    }


    formulario.addEventListener(
        "submit",
        (evento) => {
            for (
                let numeroPaso = 1;
                numeroPaso <= totalPasos;
                numeroPaso += 1
            ) {
                if (!validarPaso(numeroPaso)) {
                    evento.preventDefault();

                    mostrarPaso(numeroPaso);

                    return;
                }
            }

            botonConfirmar.disabled = true;
            botonConfirmar.textContent =
                "Procesando agendamiento...";
        }
    );


    function obtenerPasoConErrores() {
        const pasosConErrores = pasos.filter(
            (paso) => paso.querySelector(
                ".error-campo, .error-bloque"
            )
        );

        if (!pasosConErrores.length) {
            return null;
        }

        return Number(
            pasosConErrores[0].dataset.paso
        );
    }


    async function restaurarDatosIniciales() {
        actualizarMetodoPago();
        actualizarResumen();

        const tarjetaEspecialidad =
            document.querySelector(
                `[data-especialidad-id="${especialidadInicial}"]`
            );

        if (
            especialidadInicial
            && tarjetaEspecialidad
        ) {
            await seleccionarEspecialidad(
                especialidadInicial,
                tarjetaEspecialidad.dataset
                    .especialidadNombre,
                {
                    profesionalInicial,
                    fechaInicial,
                    horaInicial,
                }
            );
        }

        const pasoConErrores =
            obtenerPasoConErrores();

        if (pasoConErrores) {
            mostrarPaso(pasoConErrores);
        } else {
            mostrarPaso(1);
        }
    }


    restaurarDatosIniciales();
});
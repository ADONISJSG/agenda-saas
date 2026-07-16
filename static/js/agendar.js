document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById(
        "formulario-agendar"
    );

    if (!formulario) {
        return;
    }

    const pasos = Array.from(
        document.querySelectorAll(
            ".paso-formulario"
        )
    );

    const indicadores = Array.from(
        document.querySelectorAll(
            ".indicador-paso"
        )
    );

    const tarjetasOpciones = Array.from(
        document.querySelectorAll(
            ".tarjeta-opcion"
        )
    );

    const botonesSiguiente = Array.from(
        document.querySelectorAll(
            "[data-siguiente]"
        )
    );

    const botonesAnterior = Array.from(
        document.querySelectorAll(
            "[data-anterior]"
        )
    );

    const detalleTransferencia = (
        document.getElementById(
            "detalle-transferencia"
        )
    );

    const detalleTarjeta = (
        document.getElementById(
            "detalle-tarjeta"
        )
    );

    const resumenServicio = (
        document.getElementById(
            "resumen-servicio"
        )
    );

    const resumenTotal = (
        document.getElementById(
            "resumen-total"
        )
    );

    const resumenAnticipo = (
        document.getElementById(
            "resumen-anticipo"
        )
    );

    const resumenSaldo = (
        document.getElementById(
            "resumen-saldo"
        )
    );

    let pasoActual = 1;

    /*
    =====================================
    FUNCIONES GENERALES
    =====================================
    */

    function obtenerRadioSeleccionado(nombre) {
        return formulario.querySelector(
            `input[name="${nombre}"]:checked`
        );
    }

    function mostrarMensaje(mensaje) {
        window.alert(mensaje);
    }

    function mostrarPaso(numeroPaso) {
        pasoActual = numeroPaso;

        pasos.forEach((paso) => {
            const numero = Number(
                paso.dataset.paso
            );

            paso.classList.toggle(
                "activo",
                numero === numeroPaso
            );
        });

        indicadores.forEach((indicador) => {
            const numero = Number(
                indicador.dataset.indicador
            );

            indicador.classList.toggle(
                "activo",
                numero === numeroPaso
            );

            indicador.classList.toggle(
                "completado",
                numero < numeroPaso
            );
        });

        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    }

    function enfocarCampo(campo) {
        if (!campo) {
            return;
        }

        campo.focus();
        campo.reportValidity();
    }

    /*
    =====================================
    VALIDACIONES DEL PASO 1
    =====================================
    */

    function validarDatosPaciente() {
        const nombres = document.getElementById(
            "id_nombres"
        );

        const apellidos = document.getElementById(
            "id_apellidos"
        );

        const cedula = document.getElementById(
            "id_cedula"
        );

        const celular = document.getElementById(
            "id_celular"
        );

        const correo = document.getElementById(
            "id_correo"
        );

        if (!nombres.value.trim()) {
            mostrarMensaje(
                "Ingresa los nombres completos."
            );

            enfocarCampo(nombres);
            return false;
        }

        if (!apellidos.value.trim()) {
            mostrarMensaje(
                "Ingresa los apellidos completos."
            );

            enfocarCampo(apellidos);
            return false;
        }

        const cedulaLimpia = (
            cedula.value.replace(
                /\D/g,
                ""
            )
        );

        cedula.value = cedulaLimpia;

        if (cedulaLimpia.length !== 10) {
            mostrarMensaje(
                "La cédula debe tener exactamente 10 dígitos."
            );

            enfocarCampo(cedula);
            return false;
        }

        const celularLimpio = (
            celular.value.replace(
                /\D/g,
                ""
            )
        );

        celular.value = celularLimpio;

        if (
            celularLimpio.length !== 10
            || !celularLimpio.startsWith("09")
        ) {
            mostrarMensaje(
                "Ingresa un celular ecuatoriano válido que comience con 09."
            );

            enfocarCampo(celular);
            return false;
        }

        if (
            correo.value.trim()
            && !correo.checkValidity()
        ) {
            mostrarMensaje(
                "Ingresa un correo electrónico válido."
            );

            enfocarCampo(correo);
            return false;
        }

        return true;
    }

    /*
    =====================================
    VALIDACIONES POR PASO
    =====================================
    */

    function validarPaso(numeroPaso) {
        if (numeroPaso === 1) {
            return validarDatosPaciente();
        }

        if (numeroPaso === 2) {
            const especialidad = (
                obtenerRadioSeleccionado(
                    "especialidad"
                )
            );

            const servicio = (
                obtenerRadioSeleccionado(
                    "servicio"
                )
            );

            if (!especialidad) {
                mostrarMensaje(
                    "Selecciona una especialidad."
                );

                return false;
            }

            if (!servicio) {
                mostrarMensaje(
                    "Selecciona un servicio."
                );

                return false;
            }

            return true;
        }

        if (numeroPaso === 3) {
            const profesional = (
                obtenerRadioSeleccionado(
                    "profesional"
                )
            );

            if (!profesional) {
                mostrarMensaje(
                    "Selecciona un profesional."
                );

                return false;
            }

            return true;
        }

        if (numeroPaso === 4) {
            const fecha = document.getElementById(
                "id_fecha"
            );

            const hora = document.getElementById(
                "id_hora"
            );

            if (!fecha.value) {
                mostrarMensaje(
                    "Selecciona la fecha de la cita."
                );

                enfocarCampo(fecha);
                return false;
            }

            const fechaSeleccionada = new Date(
                `${fecha.value}T00:00:00`
            );

            const fechaActual = new Date();

            fechaActual.setHours(
                0,
                0,
                0,
                0
            );

            if (
                fechaSeleccionada
                < fechaActual
            ) {
                mostrarMensaje(
                    "La fecha de la cita no puede estar en el pasado."
                );

                enfocarCampo(fecha);
                return false;
            }

            if (!hora.value) {
                mostrarMensaje(
                    "Selecciona la hora de la cita."
                );

                enfocarCampo(hora);
                return false;
            }

            return true;
        }

        if (numeroPaso === 5) {
            const metodoPago = (
                obtenerRadioSeleccionado(
                    "metodo_pago"
                )
            );

            if (!metodoPago) {
                mostrarMensaje(
                    "Selecciona un método de pago."
                );

                return false;
            }

            if (
                metodoPago.value
                === "TRANSFERENCIA"
            ) {
                const referencia = (
                    document.getElementById(
                        "id_referencia_pago"
                    )
                );

                if (!referencia.value.trim()) {
                    mostrarMensaje(
                        "Ingresa la referencia de la transferencia."
                    );

                    enfocarCampo(referencia);
                    return false;
                }
            }

            return true;
        }

        return true;
    }

    /*
    =====================================
    SELECCIÓN DE TARJETAS
    =====================================
    */

    function marcarTarjetaSeleccionada(
        tarjeta
    ) {
        const tipo = tarjeta.dataset.tipo;

        tarjetasOpciones
            .filter(
                (opcion) => (
                    opcion.dataset.tipo
                    === tipo
                )
            )
            .forEach((opcion) => {
                opcion.classList.remove(
                    "seleccionada"
                );
            });

        tarjeta.classList.add(
            "seleccionada"
        );

        const radio = tarjeta.querySelector(
            'input[type="radio"]'
        );

        if (radio) {
            radio.checked = true;

            radio.dispatchEvent(
                new Event(
                    "change",
                    {
                        bubbles: true,
                    }
                )
            );
        }
    }

    /*
    =====================================
    FILTRAR SERVICIOS Y PROFESIONALES
    =====================================
    */

    function filtrarPorEspecialidad(
        especialidadId
    ) {
        const opcionesFiltrables = (
            document.querySelectorAll(
                ".opcion-filtrable"
            )
        );

        opcionesFiltrables.forEach(
            (opcion) => {
                const coincide = (
                    opcion.dataset.especialidad
                    === especialidadId
                );

                opcion.classList.toggle(
                    "oculto",
                    !coincide
                );

                if (!coincide) {
                    opcion.classList.remove(
                        "seleccionada"
                    );

                    const radio = (
                        opcion.querySelector(
                            'input[type="radio"]'
                        )
                    );

                    if (radio) {
                        radio.checked = false;
                    }
                }
            }
        );

        actualizarResumenPago();
    }

    /*
    =====================================
    RESUMEN Y CÁLCULO DEL PAGO
    =====================================
    */

    function actualizarResumenPago() {
        const servicioSeleccionado = (
            obtenerRadioSeleccionado(
                "servicio"
            )
        );

        if (!servicioSeleccionado) {
            resumenServicio.textContent = (
                "Sin seleccionar"
            );

            resumenTotal.textContent = (
                "$0.00"
            );

            resumenAnticipo.textContent = (
                "$0.00"
            );

            resumenSaldo.textContent = (
                "$0.00"
            );

            return;
        }

        const tarjetaServicio = (
            servicioSeleccionado.closest(
                ".tarjeta-opcion"
            )
        );

        if (!tarjetaServicio) {
            return;
        }

        const nombreServicio = (
            tarjetaServicio.dataset.nombre
        );

        const precioTexto = (
            tarjetaServicio.dataset.precio
                .replace(",", ".")
        );

        const precio = Number(
            precioTexto
        );

        const anticipo = precio * 0.20;
        const saldo = precio - anticipo;

        resumenServicio.textContent = (
            nombreServicio
        );

        resumenTotal.textContent = (
            `$${precio.toFixed(2)}`
        );

        resumenAnticipo.textContent = (
            `$${anticipo.toFixed(2)}`
        );

        resumenSaldo.textContent = (
            `$${saldo.toFixed(2)}`
        );
    }

    /*
    =====================================
    MÉTODOS DE PAGO
    =====================================
    */

    function actualizarMetodoPago() {
        const metodoSeleccionado = (
            obtenerRadioSeleccionado(
                "metodo_pago"
            )
        );

        detalleTransferencia.classList.add(
            "oculto"
        );

        detalleTarjeta.classList.add(
            "oculto"
        );

        if (!metodoSeleccionado) {
            return;
        }

        if (
            metodoSeleccionado.value
            === "TRANSFERENCIA"
        ) {
            detalleTransferencia.classList.remove(
                "oculto"
            );
        }

        if (
            metodoSeleccionado.value
            === "TARJETA"
        ) {
            detalleTarjeta.classList.remove(
                "oculto"
            );
        }
    }

    /*
    =====================================
    EVENTOS DE LAS TARJETAS
    =====================================
    */

    tarjetasOpciones.forEach(
        (tarjeta) => {
            tarjeta.addEventListener(
                "click",
                () => {
                    marcarTarjetaSeleccionada(
                        tarjeta
                    );

                    if (
                        tarjeta.dataset.tipo
                        === "especialidad"
                    ) {
                        filtrarPorEspecialidad(
                            tarjeta.dataset.id
                        );
                    }

                    if (
                        tarjeta.dataset.tipo
                        === "servicio"
                    ) {
                        actualizarResumenPago();
                    }
                }
            );
        }
    );

    /*
    =====================================
    BOTONES SIGUIENTE Y ATRÁS
    =====================================
    */

    botonesSiguiente.forEach(
        (boton) => {
            boton.addEventListener(
                "click",
                () => {
                    if (
                        !validarPaso(
                            pasoActual
                        )
                    ) {
                        return;
                    }

                    const siguientePaso = Number(
                        boton.dataset.siguiente
                    );

                    mostrarPaso(
                        siguientePaso
                    );
                }
            );
        }
    );

    botonesAnterior.forEach(
        (boton) => {
            boton.addEventListener(
                "click",
                () => {
                    const pasoAnterior = Number(
                        boton.dataset.anterior
                    );

                    mostrarPaso(
                        pasoAnterior
                    );
                }
            );
        }
    );

    /*
    =====================================
    CAMBIO DE MÉTODO DE PAGO
    =====================================
    */

    const radiosMetodoPago = (
        formulario.querySelectorAll(
            'input[name="metodo_pago"]'
        )
    );

    radiosMetodoPago.forEach(
        (radio) => {
            radio.addEventListener(
                "change",
                actualizarMetodoPago
            );
        }
    );

    /*
    =====================================
    LIMPIEZA DE CAMPOS NUMÉRICOS
    =====================================
    */

    const campoCedula = (
        document.getElementById(
            "id_cedula"
        )
    );

    const campoCelular = (
        document.getElementById(
            "id_celular"
        )
    );

    campoCedula.addEventListener(
        "input",
        () => {
            campoCedula.value = (
                campoCedula.value
                    .replace(
                        /\D/g,
                        ""
                    )
                    .slice(
                        0,
                        10
                    )
            );
        }
    );

    campoCelular.addEventListener(
        "input",
        () => {
            campoCelular.value = (
                campoCelular.value
                    .replace(
                        /\D/g,
                        ""
                    )
                    .slice(
                        0,
                        10
                    )
            );
        }
    );

    /*
    =====================================
    ENVÍO FINAL
    =====================================
    */

    formulario.addEventListener(
        "submit",
        (evento) => {
            for (
                let numeroPaso = 1;
                numeroPaso <= 5;
                numeroPaso += 1
            ) {
                if (
                    !validarPaso(
                        numeroPaso
                    )
                ) {
                    evento.preventDefault();

                    mostrarPaso(
                        numeroPaso
                    );

                    return;
                }
            }

            const botonFinal = (
                formulario.querySelector(
                    'button[type="submit"]'
                )
            );

            if (botonFinal) {
                botonFinal.disabled = true;
                botonFinal.textContent = (
                    "Procesando cita..."
                );
            }
        }
    );

    /*
    =====================================
    ESTADO INICIAL
    =====================================
    */

    const especialidadSeleccionada = (
        obtenerRadioSeleccionado(
            "especialidad"
        )
    );

    if (especialidadSeleccionada) {
        const tarjetaEspecialidad = (
            especialidadSeleccionada.closest(
                ".tarjeta-opcion"
            )
        );

        if (tarjetaEspecialidad) {
            tarjetaEspecialidad.classList.add(
                "seleccionada"
            );

            filtrarPorEspecialidad(
                tarjetaEspecialidad.dataset.id
            );
        }
    } else {
        document
            .querySelectorAll(
                ".opcion-filtrable"
            )
            .forEach((opcion) => {
                opcion.classList.add(
                    "oculto"
                );
            });
    }

    formulario
        .querySelectorAll(
            'input[type="radio"]:checked'
        )
        .forEach((radio) => {
            const tarjeta = radio.closest(
                ".tarjeta-opcion"
            );

            if (tarjeta) {
                tarjeta.classList.add(
                    "seleccionada"
                );
            }
        });

    actualizarResumenPago();
    actualizarMetodoPago();
    mostrarPaso(1);
});
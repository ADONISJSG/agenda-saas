document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById(
        "formulario-agendamiento"
    );

    const contenedorAgendamiento = document.getElementById(
        "contenedor-agendamiento"
    );

    const campoEspecialidad = document.getElementById(
        "id_especialidad"
    );

    const campoProfesional = document.getElementById(
        "id_profesional"
    );

    const datosTransferencia = document.getElementById(
        "datos-transferencia"
    );

    const contenedorReferencia = document.getElementById(
        "contenedor-referencia"
    );

    const campoReferencia = document.getElementById(
        "id_referencia_pago"
    );

    const resumenAnticipo = document.getElementById(
        "resumen-anticipo"
    );

    const montoTransferencia = document.getElementById(
        "monto-transferencia"
    );

    const datoBanco = document.getElementById(
        "dato-banco"
    );

    const datoTipoCuenta = document.getElementById(
        "dato-tipo-cuenta"
    );

    const datoNumeroCuenta = document.getElementById(
        "dato-numero-cuenta"
    );

    const datoTitular = document.getElementById(
        "dato-titular"
    );

    const datoIdentificacion = document.getElementById(
        "dato-identificacion"
    );

    const avisoTransferencia = document.getElementById(
        "aviso-transferencia"
    );

    const avisoTarjeta = document.getElementById(
        "aviso-tarjeta"
    );

    if (
        !formulario
        || !contenedorAgendamiento
        || !datosTransferencia
    ) {
        return;
    }


    const urlProfesionales =
        contenedorAgendamiento.dataset.urlProfesionales;

    const opcionesPago = formulario.querySelector(
        ".opciones-pago"
    );

    const radioTransferencia = formulario.querySelector(
        'input[name="metodo_pago"][value="TRANSFERENCIA"]'
    );

    const tarjetaTransferencia = radioTransferencia
        ? radioTransferencia.closest(".tarjeta-pago")
        : null;


    let transferenciaActual = {
        habilitada: false,
        banco: "",
        tipo_cuenta: "",
        numero_cuenta: "",
        titular: "",
        identificacion: "",
    };

    let solicitudActual = 0;


    function profesionalSeleccionado() {
        return Boolean(
            campoProfesional
            && campoProfesional.value
        );
    }


    function crearMensajeNoDisponible() {
        if (!opcionesPago) {
            return null;
        }

        let mensaje = document.getElementById(
            "mensaje-transferencia-no-disponible"
        );

        if (mensaje) {
            return mensaje;
        }

        mensaje = document.createElement("div");

        mensaje.id =
            "mensaje-transferencia-no-disponible";

        mensaje.className =
            "mensaje-transferencia-no-disponible oculto";

        mensaje.innerHTML = `
            <span>ℹ️</span>

            <p>
                Este profesional no tiene habilitado
                el pago mediante transferencia.
                Puedes continuar con tarjeta.
            </p>
        `;

        opcionesPago.after(mensaje);

        return mensaje;
    }


    const mensajeNoDisponible =
        crearMensajeNoDisponible();


    function obtenerMetodoSeleccionado() {
        return formulario.querySelector(
            'input[name="metodo_pago"]:checked'
        );
    }


    function limpiarDatosVisibles() {
        if (datoBanco) {
            datoBanco.textContent = "No disponible";
        }

        if (datoTipoCuenta) {
            datoTipoCuenta.textContent =
                "No disponible";
        }

        if (datoNumeroCuenta) {
            datoNumeroCuenta.textContent =
                "No disponible";
        }

        if (datoTitular) {
            datoTitular.textContent =
                "No disponible";
        }

        if (datoIdentificacion) {
            datoIdentificacion.textContent =
                "No disponible";
        }
    }


    function colocarDatosVisibles(transferencia) {
        if (datoBanco) {
            datoBanco.textContent =
                transferencia.banco
                || "No disponible";
        }

        if (datoTipoCuenta) {
            datoTipoCuenta.textContent =
                transferencia.tipo_cuenta
                || "No disponible";
        }

        if (datoNumeroCuenta) {
            datoNumeroCuenta.textContent =
                transferencia.numero_cuenta
                || "No disponible";
        }

        if (datoTitular) {
            datoTitular.textContent =
                transferencia.titular
                || "No disponible";
        }

        if (datoIdentificacion) {
            datoIdentificacion.textContent =
                transferencia.identificacion
                || "No disponible";
        }
    }


    function actualizarMontoTransferencia() {
        if (!montoTransferencia) {
            return;
        }

        const valor = resumenAnticipo
            ? resumenAnticipo.textContent.trim()
            : "0.00";

        montoTransferencia.textContent =
            valor || "0.00";
    }


    function ocultarSeccionTransferencia() {
        datosTransferencia.classList.add(
            "oculto"
        );

        contenedorReferencia?.classList.add(
            "oculto"
        );
    }


    function mostrarSeccionTransferencia() {
        datosTransferencia.classList.remove(
            "oculto"
        );

        contenedorReferencia?.classList.remove(
            "oculto"
        );

        actualizarMontoTransferencia();
    }


    function actualizarAvisosMetodoPago() {
        const seleccionado =
            obtenerMetodoSeleccionado();

        const esTransferencia =
            seleccionado?.value === "TRANSFERENCIA";

        const esTarjeta =
            seleccionado?.value === "TARJETA";

        if (avisoTransferencia) {
            avisoTransferencia.classList.toggle(
                "oculto",
                !(
                    esTransferencia
                    && transferenciaActual.habilitada
                )
            );
        }

        if (avisoTarjeta) {
            avisoTarjeta.classList.toggle(
                "oculto",
                !esTarjeta
            );
        }
    }


    function actualizarVistaMetodoPago() {
        const metodoSeleccionado =
            obtenerMetodoSeleccionado();

        const esTransferencia =
            metodoSeleccionado?.value
            === "TRANSFERENCIA";

        actualizarAvisosMetodoPago();

        if (
            esTransferencia
            && transferenciaActual.habilitada
        ) {
            mostrarSeccionTransferencia();
            return;
        }

        ocultarSeccionTransferencia();

        if (!esTransferencia && campoReferencia) {
            campoReferencia.value = "";
        }
    }


    function aplicarDisponibilidadTransferencia() {
        const habilitada = Boolean(
            transferenciaActual.habilitada
        );

        const hayProfesional =
            profesionalSeleccionado();

        tarjetaTransferencia?.classList.toggle(
            "oculto",
            !habilitada
        );

        mensajeNoDisponible?.classList.toggle(
            "oculto",
            !(
                hayProfesional
                && !habilitada
            )
        );

        if (habilitada) {
            colocarDatosVisibles(
                transferenciaActual
            );
        } else {
            limpiarDatosVisibles();

            if (
                radioTransferencia
                && radioTransferencia.checked
            ) {
                radioTransferencia.checked = false;

                if (campoReferencia) {
                    campoReferencia.value = "";
                }
            }
        }

        actualizarVistaMetodoPago();
    }


    function reiniciarTransferencia() {
        transferenciaActual = {
            habilitada: false,
            banco: "",
            tipo_cuenta: "",
            numero_cuenta: "",
            titular: "",
            identificacion: "",
        };

        aplicarDisponibilidadTransferencia();
    }


    async function cargarTransferenciaProfesional() {
        const especialidadId =
            campoEspecialidad?.value || "";

        const profesionalId =
            campoProfesional?.value || "";

        if (
            !urlProfesionales
            || !especialidadId
            || !profesionalId
        ) {
            reiniciarTransferencia();
            return;
        }

        const numeroSolicitud =
            ++solicitudActual;

        try {
            const parametros = new URLSearchParams({
                especialidad_id:
                    String(especialidadId),
            });

            const respuesta = await fetch(
                `${urlProfesionales}?${parametros}`
            );

            const datos = await respuesta.json();

            if (numeroSolicitud !== solicitudActual) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error(
                    datos.error
                    || "No se pudieron consultar los datos de pago."
                );
            }

            const profesional =
                datos.profesionales.find(
                    (elemento) =>
                        String(elemento.id)
                        === String(profesionalId)
                );

            if (
                !profesional
                || !profesional.transferencia
            ) {
                reiniciarTransferencia();
                return;
            }

            transferenciaActual = {
                habilitada: Boolean(
                    profesional.transferencia.habilitada
                ),

                banco:
                    profesional.transferencia.banco
                    || "",

                tipo_cuenta:
                    profesional.transferencia.tipo_cuenta
                    || "",

                numero_cuenta:
                    profesional.transferencia.numero_cuenta
                    || "",

                titular:
                    profesional.transferencia.titular
                    || "",

                identificacion:
                    profesional.transferencia.identificacion
                    || "",
            };

            aplicarDisponibilidadTransferencia();

        } catch (error) {
            console.error(
                "Error cargando transferencia:",
                error
            );

            reiniciarTransferencia();
        }
    }


    formulario
        .querySelectorAll(
            'input[name="metodo_pago"]'
        )
        .forEach((radio) => {
            radio.addEventListener(
                "change",
                actualizarVistaMetodoPago
            );
        });


    document.addEventListener(
        "click",
        (evento) => {
            const tarjetaProfesional =
                evento.target.closest(
                    ".tarjeta-profesional"
                );

            if (tarjetaProfesional) {
                window.setTimeout(
                    cargarTransferenciaProfesional,
                    80
                );

                return;
            }

            const tarjetaEspecialidad =
                evento.target.closest(
                    ".tarjeta-especialidad"
                );

            if (tarjetaEspecialidad) {
                window.setTimeout(
                    reiniciarTransferencia,
                    30
                );

                return;
            }

            const botonSiguiente =
                evento.target.closest(
                    "[data-siguiente]"
                );

            if (botonSiguiente) {
                window.setTimeout(
                    cargarTransferenciaProfesional,
                    120
                );
            }
        }
    );


    if (resumenAnticipo) {
        const observadorMonto =
            new MutationObserver(
                actualizarMontoTransferencia
            );

        observadorMonto.observe(
            resumenAnticipo,
            {
                childList: true,
                characterData: true,
                subtree: true,
            }
        );
    }


    async function copiarTexto(texto) {
        if (
            navigator.clipboard
            && window.isSecureContext
        ) {
            await navigator.clipboard.writeText(
                texto
            );

            return;
        }

        const campoTemporal =
            document.createElement("textarea");

        campoTemporal.value = texto;
        campoTemporal.style.position = "fixed";
        campoTemporal.style.opacity = "0";

        document.body.appendChild(
            campoTemporal
        );

        campoTemporal.select();

        document.execCommand("copy");

        campoTemporal.remove();
    }


    document
        .querySelectorAll("[data-copiar]")
        .forEach((boton) => {
            boton.addEventListener(
                "click",
                async () => {
                    const idElemento =
                        boton.dataset.copiar;

                    const elemento =
                        document.getElementById(
                            idElemento
                        );

                    if (!elemento) {
                        return;
                    }

                    const texto =
                        elemento.textContent.trim();

                    if (
                        !texto
                        || texto === "No disponible"
                    ) {
                        return;
                    }

                    const textoOriginal =
                        boton.textContent;

                    try {
                        await copiarTexto(texto);

                        boton.textContent = "Copiado";

                        boton.classList.add(
                            "copiado"
                        );

                        window.setTimeout(() => {
                            boton.textContent =
                                textoOriginal;

                            boton.classList.remove(
                                "copiado"
                            );
                        }, 1600);

                    } catch (error) {
                        boton.textContent =
                            "No se pudo copiar";

                        window.setTimeout(() => {
                            boton.textContent =
                                textoOriginal;
                        }, 1600);
                    }
                }
            );
        });


    actualizarMontoTransferencia();
    reiniciarTransferencia();
    cargarTransferenciaProfesional();
});
<?php
/**
 * Formulario de contacto de apprubric.net: envía el mensaje a apprubricnic@gmail.com.
 *
 * Protecciones: campo trampa para robots (sitio_web), tiempo mínimo de llenado,
 * un envío por minuto por IP, límites de largo y limpieza de saltos de línea en
 * los encabezados (evita que alguien use el formulario para mandar correo a terceros).
 * Responde JSON si la página lo pide con fetch; si no, vuelve a la página.
 */

const DESTINO = 'apprubricnic@gmail.com';
const REMITENTE = 'no-reply@apprubric.net';
const ESPERA_SEGUNDOS = 60;

function responder(int $codigo, string $mensaje): void
{
    $quiereJson = str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');
    if ($quiereJson) {
        http_response_code($codigo);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['message' => $mensaje], JSON_UNESCAPED_UNICODE);
    } else {
        header('Location: /' . ($codigo === 200 ? '?enviado=1' : '') . '#contacto', true, 303);
    }
    exit;
}

function campo(string $nombre, int $max): string
{
    $valor = trim((string) ($_POST[$nombre] ?? ''));
    $valor = preg_replace('/[^\P{C}\n\t]/u', '', $valor) ?? '';

    return mb_substr($valor, 0, $max);
}

function linea(string $texto): string
{
    return trim(preg_replace('/[\r\n]+/', ' ', $texto) ?? '');
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: /#contacto', true, 303);
    exit;
}

// Robots: llenan el campo trampa o envían en menos de 3 segundos. Se les responde "enviado".
$t = (int) ($_POST['t'] ?? 0);
if (campo('sitio_web', 200) !== '' || ($t > 0 && time() - $t < 3)) {
    responder(200, 'Mensaje enviado. Le responderemos pronto.');
}

$nombre = linea(campo('nombre', 120));
$correo = linea(campo('correo', 160));
$centro = linea(campo('centro', 160));
$telefono = linea(campo('telefono', 40));
$mensaje = campo('mensaje', 3000);

if ($nombre === '' || $centro === '' || $mensaje === '') {
    responder(422, 'Complete nombre, correo, centro educativo y mensaje.');
}
if (! filter_var($correo, FILTER_VALIDATE_EMAIL)) {
    responder(422, 'Revise el correo: debe tener la forma nombre@dominio.com.');
}

// Un envío por minuto desde la misma dirección.
$marca = sys_get_temp_dir() . '/apprubric_contacto_' . hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'x');
if (is_file($marca) && time() - (int) @filemtime($marca) < ESPERA_SEGUNDOS) {
    responder(429, 'Ya recibimos un mensaje suyo hace un momento. Espere un minuto para enviar otro.');
}

$cuerpo = "Mensaje desde el formulario de apprubric.net\n\n"
    . "Nombre: {$nombre}\n"
    . "Correo: {$correo}\n"
    . "Centro educativo: {$centro}\n"
    . 'Teléfono: ' . ($telefono !== '' ? $telefono : '(no indicó)') . "\n\n"
    . "Mensaje:\n{$mensaje}\n";

$asunto = '=?UTF-8?B?' . base64_encode('AppRubric: mensaje de ' . $nombre . ' (' . $centro . ')') . '?=';
$encabezados = implode("\r\n", [
    'From: AppRubric <' . REMITENTE . '>',
    'Reply-To: ' . $correo,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);

if (! mail(DESTINO, $asunto, $cuerpo, $encabezados, '-f' . REMITENTE)) {
    responder(500, 'No se pudo enviar el mensaje. Escríbanos por WhatsApp al +505 5819 6269.');
}

@touch($marca);
responder(200, 'Mensaje enviado. Le responderemos pronto.');

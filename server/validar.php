<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['valida' => false, 'mensaje' => 'Método no permitido']);
    exit;
}

$body = json_decode(file_get_contents('php://input'), true);
$clave = strtoupper(trim($body['clave'] ?? ''));
$machine_id = $body['machine_id'] ?? '';

if ($clave === '') {
    http_response_code(400);
    echo json_encode(['valida' => false, 'mensaje' => 'Clave requerida']);
    exit;
}

$archivo = __DIR__ . '/licencias.json';
if (!file_exists($archivo)) {
    echo json_encode(['valida' => false, 'mensaje' => 'Sin licencias configuradas']);
    exit;
}

$licencias = json_decode(file_get_contents($archivo), true);

if (!isset($licencias[$clave])) {
    echo json_encode(['valida' => false, 'mensaje' => 'Clave no encontrada']);
    exit;
}

$licencia = $licencias[$clave];

if (!($licencia['activa'] ?? true)) {
    echo json_encode(['valida' => false, 'mensaje' => 'Licencia desactivada']);
    exit;
}

echo json_encode(['valida' => true, 'mensaje' => 'OK']);

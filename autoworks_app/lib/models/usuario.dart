class Usuario {
  final String id;
  final String nombres;
  final String apellidos;
  final String email;
  final String tipo;
  final bool activo;
  final String? telefono;
  final String? fotoPerfil;

  Usuario({
    required this.id,
    required this.nombres,
    required this.apellidos,
    required this.email,
    required this.tipo,
    required this.activo,
    this.telefono,
    this.fotoPerfil,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) => Usuario(
    id:          json['id'],
    nombres:     json['nombres'],
    apellidos:   json['apellidos'],
    email:       json['email'],
    tipo:        json['tipo'],
    activo:      json['activo'],
    telefono:    json['telefono'],
    fotoPerfil:  json['foto_perfil_url'],
  );

  String get nombreCompleto => '$nombres $apellidos';
  String get iniciales =>
    '${nombres.isNotEmpty ? nombres[0] : ''}${apellidos.isNotEmpty ? apellidos[0] : ''}'.toUpperCase();
}
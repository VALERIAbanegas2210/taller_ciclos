import 'package:flutter/material.dart';
import '../../models/usuario.dart';
import '../../services/auth_service.dart';
import '../login/login_screen.dart';

class PerfilScreen extends StatefulWidget {
  const PerfilScreen({super.key});
  @override
  State<PerfilScreen> createState() => _PerfilScreenState();
}

class _PerfilScreenState extends State<PerfilScreen> {
  final _auth    = AuthService();
  Usuario? _usuario;
  bool _cargando = true;

  static const _blue = Color(0xFF1E3A8A);
  static const _red  = Color(0xFFDC2626);

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    final u = await _auth.getUsuario();
    if (mounted) setState(() { _usuario = u; _cargando = false; });
  }

  Future<void> _logout() async {
    await _auth.logout();
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  String get _rolLabel {
    switch (_usuario?.tipo) {
      case 'admin':   return 'Administrador';
      case 'tecnico': return 'Técnico';
      case 'taller':  return 'Taller';
      default:        return 'Cliente';
    }
  }

  Color get _rolColor {
    switch (_usuario?.tipo) {
      case 'admin':   return const Color(0xFF7C3AED);
      case 'tecnico': return const Color(0xFF0891B2);
      case 'taller':  return const Color(0xFF059669);
      default:        return _blue;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text('Mi perfil',
          style: TextStyle(color: Color(0xFF0F172A), fontSize: 17, fontWeight: FontWeight.w600)),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded, color: Color(0xFF64748B)),
            onPressed: _logout,
            tooltip: 'Cerrar sesión',
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: const Color(0xFFE2E8F0)),
        ),
      ),
      body: _cargando
        ? const Center(child: CircularProgressIndicator())
        : _usuario == null
          ? const Center(child: Text('No se encontró el usuario'))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [

                  // Avatar
                  Container(
                    width: 88, height: 88,
                    decoration: BoxDecoration(
                      color: _blue.withOpacity(0.1),
                      shape: BoxShape.circle,
                      border: Border.all(color: _blue.withOpacity(0.2), width: 2),
                    ),
                    child: _usuario!.fotoPerfil != null
                      ? ClipOval(child: Image.network(_usuario!.fotoPerfil!, fit: BoxFit.cover))
                      : Center(
                          child: Text(
                            _usuario!.iniciales,
                            style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700, color: _blue),
                          ),
                        ),
                  ),
                  const SizedBox(height: 12),
                  Text(_usuario!.nombreCompleto,
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: _rolColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: _rolColor.withOpacity(0.2)),
                    ),
                    child: Text(_rolLabel,
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: _rolColor)),
                  ),
                  const SizedBox(height: 24),

                  // Info card
                  _InfoCard(usuario: _usuario!),
                  const SizedBox(height: 16),

                  // Estado
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          _usuario!.activo ? Icons.check_circle : Icons.cancel,
                          color: _usuario!.activo ? const Color(0xFF16A34A) : _red,
                          size: 20,
                        ),
                        const SizedBox(width: 10),
                        Text(
                          _usuario!.activo ? 'Cuenta activa' : 'Cuenta inactiva',
                          style: TextStyle(
                            fontSize: 14, fontWeight: FontWeight.w500,
                            color: _usuario!.activo ? const Color(0xFF16A34A) : _red,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Logout
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: OutlinedButton.icon(
                      onPressed: _logout,
                      icon: const Icon(Icons.logout_rounded, size: 18),
                      label: const Text('Cerrar sesión'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: _red,
                        side: BorderSide(color: _red.withOpacity(0.4)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final Usuario usuario;
  const _InfoCard({required this.usuario});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        children: [
          _fila(Icons.email_outlined,    'Correo',   usuario.email),
          if (usuario.telefono != null)
            _fila(Icons.phone_outlined,  'Teléfono', usuario.telefono!),
          _fila(Icons.badge_outlined,    'ID',       usuario.id.substring(0, 8).toUpperCase()),
        ],
      ),
    );
  }

  Widget _fila(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: const Color(0xFF64748B)),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
              Text(value,  style: const TextStyle(fontSize: 13, color: Color(0xFF0F172A), fontWeight: FontWeight.w500)),
            ],
          ),
        ],
      ),
    );
  }
}
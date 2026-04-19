import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';
import '../models/usuario.dart';

class AuthService {
  static const _tokenKey   = 'token';
  static const _usuarioKey = 'usuario';

  Future<Map<String, dynamic>> login(String email, String password) async {
    final res = await http.post(
      Uri.parse('${AppConstants.baseUrl}/usuarios/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey,   data['access_token']);
      await prefs.setString(_usuarioKey, jsonEncode(data['usuario']));
      return {'ok': true, 'usuario': Usuario.fromJson(data['usuario'])};
    } else {
      final error = jsonDecode(res.body);
      return {'ok': false, 'mensaje': error['detail'] ?? 'Error al iniciar sesión'};
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<Usuario?> getUsuario() async {
    final prefs = await SharedPreferences.getInstance();
    final str   = prefs.getString(_usuarioKey);
    if (str == null) return null;
    return Usuario.fromJson(jsonDecode(str));
  }

  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  Future<Map<String, String>> getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type':  'application/json',
      'Authorization': 'Bearer $token',
    };
  }
}
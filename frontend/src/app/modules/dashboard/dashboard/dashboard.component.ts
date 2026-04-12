import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { BitacoraComponent } from '../bitacora/bitacora.component';
import { ReporteComponent } from '../reporte/reporte.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, BitacoraComponent, ReporteComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  usuario: any = null;
  seccionActiva = 'inicio';

  menuItems = [
    { id: 'inicio',    icono: '⊞',  label: 'Inicio' },
    { id: 'taller',    icono: '🔧', label: 'Taller' },
    { id: 'pedidos',   icono: '📋', label: 'Pedidos' },
    { id: 'bitacora',  icono: '📖', label: 'Bitácora' },
    { id: 'reporte',   icono: '📊', label: 'Reporte' },
  ];

  agenda = [
    { hora: '10:00', fin: '13:00', titulo: 'Cita de vehículo', auto: 'Toyota Corolla' },
    { hora: '13:00', fin: '17:30', titulo: 'Cita de vehículo', auto: 'Honda Civic' },
    { hora: '15:00', fin: '18:00', titulo: 'Cita de vehículo', auto: 'Nissan Sentra' },
  ];

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.usuario = this.authService.getUsuario();
    if (!this.usuario) this.router.navigate(['/login']);
  }

  get nombreCompleto() {
    return this.usuario ? `${this.usuario.nombres} ${this.usuario.apellidos}` : 'Usuario';
  }

  get rolLabel() {
    const roles: any = { admin: 'Administrador', tecnico: 'Técnico', cliente: 'Cliente' };
    return roles[this.usuario?.tipo] || this.usuario?.tipo;
  }

  get iniciales() {
    if (!this.usuario) return 'U';
    return `${this.usuario.nombres[0]}${this.usuario.apellidos[0]}`.toUpperCase();
  }

  setSeccion(id: string) { this.seccionActiva = id; }

  logout() {
    // Llamar al endpoint de logout para registrar en bitácora
    const token = localStorage.getItem('token');
    if (token) {
      fetch('http://localhost:8000/api/usuarios/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      }).finally(() => {
        this.authService.logout();
        this.router.navigate(['/login']);
      });
    } else {
      this.authService.logout();
      this.router.navigate(['/login']);
    }
  }
}
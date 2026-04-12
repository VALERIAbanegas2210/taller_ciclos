import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-bitacora',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './bitacora.component.html',
  styleUrls: ['./bitacora.component.css']
})
export class BitacoraComponent implements OnInit {
  registros: any[] = [];
  total = 0;
  loading = true;
  error = '';

  private API = 'http://localhost:8000/api/bitacora';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.cargarBitacora();
  }

  cargarBitacora() {
    this.loading = true;
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });

    this.http.get<any>(this.API, { headers }).subscribe({
      next: (res) => {
        this.registros = res.registros;
        this.total = res.total;
        this.loading = false;
      },
      error: () => {
        this.error = 'Error al cargar la bitácora';
        this.loading = false;
      }
    });
  }

  formatFecha(fecha: string): string {
    return new Date(fecha).toLocaleString('es-BO', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  }

  getAccionClass(accion: string): string {
    return accion === 'login' ? 'badge-login' : 'badge-logout';
  }

  getTipoClass(tipo: string): string {
    const map: any = { admin: 'badge-admin', tecnico: 'badge-tecnico', cliente: 'badge-cliente' };
    return map[tipo] || '';
  }

  get totalLogin()  { return this.registros.filter(r => r.accion === 'login').length; }
  get totalLogout() { return this.registros.filter(r => r.accion === 'logout').length; }
}
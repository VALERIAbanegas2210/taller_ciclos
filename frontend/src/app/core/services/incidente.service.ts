import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http'; // Importa HttpHeaders
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class IncidenteService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  // Función privada para crear los headers con el Token
  private getHeaders() {
    const token = localStorage.getItem('token'); // Asegúrate que el nombre sea 'token'
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  crearIncidente(incidente: any): Observable<any> {
    // Pasamos los headers como tercer parámetro
    return this.http.post(`${this.apiUrl}/incidentes/`, incidente, { headers: this.getHeaders() });
  }

  getIncidentesPendientes(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/incidentes/pendientes`, { headers: this.getHeaders() });
  }

  aceptarIncidente(asignacion: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/asignaciones/`, asignacion, { headers: this.getHeaders() });
  }
}
import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { Observable } from 'rxjs';

export interface Taller {
  id:                string;
  nombre:            string;
  email:             string;
  telefono:          string | null;
  direccion:         string | null;
  radio_servicio_km: number | null;
  logo_url:          string | null;
  descripcion:       string | null;
  activo:            boolean;
  verificado:        boolean;
  comision_pct:      number;
}

export interface TallerCreate {
  nombre:            string;
  email:             string;
  password:          string;
  telefono?:         string;
  direccion?:        string;
  radio_servicio_km?: number;
  descripcion?:      string;
  latitud?:          number | null;
  longitud?:         number | null;
}

export interface TallerUpdate {
  nombre?:            string;
  telefono?:          string;
  direccion?:         string;
  radio_servicio_km?: number;
  descripcion?:       string;
  latitud?:           number | null;
  longitud?:          number | null;
}

@Injectable({ providedIn: 'root' })
export class TallerService {

  private API = 'http://localhost:8000/api/talleres';
  private isBrowser: boolean;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  private get headers(): HttpHeaders {
    const token = this.isBrowser ? localStorage.getItem('token') : '';
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  registrar(data: TallerCreate): Observable<Taller> {
    return this.http.post<Taller>(`${this.API}/registro`, data, { headers: this.headers });
  }

  obtener(tallerId: string): Observable<Taller> {
    return this.http.get<Taller>(`${this.API}/mi-taller/${tallerId}`, { headers: this.headers });
  }

  actualizar(tallerId: string, data: TallerUpdate): Observable<Taller> {
    return this.http.put<Taller>(`${this.API}/mi-taller/${tallerId}`, data, { headers: this.headers });
  }

  subirLogo(tallerId: string, logo: File): Observable<any> {
    const formData = new FormData();
    formData.append('logo', logo, logo.name);
    const token = this.isBrowser ? localStorage.getItem('token') : '';
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.post(`${this.API}/mi-taller/${tallerId}/logo`, formData, { headers });
  }

  listarActivos(): Observable<Taller[]> {
    return this.http.get<Taller[]>(`${this.API}/activos`);
  }
}
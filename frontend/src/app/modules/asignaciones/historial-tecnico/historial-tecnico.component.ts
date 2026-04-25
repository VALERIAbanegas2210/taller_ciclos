import {
  Component, OnInit, signal, computed,
  ChangeDetectionStrategy, ChangeDetectorRef,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

type TabEstado = 'pendientes' | 'proceso' | 'terminados';

interface CasoHistorial {
  asignacion_id:      string;
  incidente_id:       string;
  estado:             string;
  categoria:          string;
  prioridad:          string;
  descripcion_manual: string;
  direccion_texto:    string;
  distancia_km:       number;
  precio_cotizado:    number;
  foto_evidencia:     string;
  aceptado_at:        string;
  completado_at:      string;
  created_at:         string;
  resumen_ia:       string | null;  
  confianza_ia:     number | null;   
  requiere_revision: boolean | null; 
  vehiculo: {
    placa:  string;
    marca:  string;
    modelo: string;
    color:  string;
  } | null;
}

@Component({
  selector: 'app-historial-tecnico',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './historial-tecnico.component.html',
  styleUrls:  ['./historial-tecnico.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HistorialTecnicoComponent implements OnInit {

  tabActiva   = signal<TabEstado>('pendientes');
  casos       = signal<CasoHistorial[]>([]);
  cargando    = signal(false);
  error       = signal<string | null>(null);
  mensaje     = signal<string | null>(null);
  cambiando   = signal<string | null>(null);  // asignacion_id en proceso

  // Modal de detalle
  modalCaso   = signal<CasoHistorial | null>(null);

  readonly tabs: { id: TabEstado; label: string; icono: string }[] = [
    { id: 'pendientes', label: 'Pendientes',  icono: '⏳' },
    { id: 'proceso',    label: 'En Proceso',  icono: '🚗' },
    { id: 'terminados', label: 'Terminados',  icono: '✅' },
  ];

  constructor(
    private http: HttpClient,
    private cd:   ChangeDetectorRef,
  ) {}

  ngOnInit(): void { this.cargar(); }

  private get headers(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }

  // ── CARGAR HISTORIAL ──────────────────────────────────────────────────────

  cargar(tab?: TabEstado): void {
    if (tab) this.tabActiva.set(tab);
    this.cargando.set(true);
    this.error.set(null);

    const estado = this.tabActiva();
    const url    = `${environment.apiUrl}/asignaciones/mi-historial?estado=${estado}`;

    this.http.get<CasoHistorial[]>(url, { headers: this.headers }).subscribe({
      next: (data) => {
        this.casos.set(data);
        this.cargando.set(false);
        this.cd.markForCheck();
      },
      error: () => {
        this.error.set('Error al cargar el historial.');
        this.cargando.set(false);
        this.cd.markForCheck();
      },
    });
  }

  // ── CAMBIAR ESTADO ────────────────────────────────────────────────────────

  cambiarEstado(asignacionId: string, nuevoEstado: string, nota?: string): void {
    this.cambiando.set(asignacionId);
    this.mensaje.set(null);

    this.http.patch(
      `${environment.apiUrl}/asignaciones/${asignacionId}/estado`,
      { nuevo_estado: nuevoEstado, nota: nota ?? null },
      { headers: this.headers }
    ).subscribe({
      next: (res: any) => {
        this.mensaje.set(`✅ Estado actualizado: ${res.estado}`);
        this.cambiando.set(null);
        this.cerrarModal();
        this.cargar();  // recarga la tab actual
        this.cd.markForCheck();
      },
      error: (err) => {
        this.error.set(err?.error?.detail ?? 'Error al cambiar estado.');
        this.cambiando.set(null);
        this.cd.markForCheck();
      },
    });
  }

  // ── MODAL ─────────────────────────────────────────────────────────────────

  abrirModal(caso: CasoHistorial): void  { this.modalCaso.set(caso); }
  cerrarModal(): void                     { this.modalCaso.set(null); }

  // ── HELPERS ───────────────────────────────────────────────────────────────

  prioridadClass(p?: string): string {
    const map: Record<string, string> = {
      critica: 'badge--critica',
      alta:    'badge--alta',
      media:   'badge--media',
      baja:    'badge--baja',
    };
    return map[p ?? ''] ?? 'badge--media';
  }

  estadoClass(e: string): string {
    const map: Record<string, string> = {
      aceptada:   'estado--aceptada',
      en_camino:  'estado--proceso',
      completada: 'estado--completada',
      cancelada:  'estado--cancelada',
    };
    return map[e] ?? '';
  }

  estadoLabel(e: string): string {
    const map: Record<string, string> = {
      aceptada:   '⏳ Aceptado',
      en_camino:  '🚗 En camino',
      completada: '✅ Completado',
      cancelada:  '❌ Cancelado',
    };
    return map[e] ?? e;
  }

  getFotoUrl(ruta?: string): string {
    if (!ruta) return '';
    if (ruta.startsWith('http')) return ruta;
    return `http://localhost:8000/${ruta.replace(/\\/g, '/')}`;
  }

  // Botones de acción según el estado actual
  accionesPosibles(estado: string): { label: string; estado: string; clase: string }[] {
    if (estado === 'aceptada') {
      return [
        { label: '🚗 Ir en camino', estado: 'en_camino',  clase: 'btn-proceso' },
        { label: '❌ Cancelar',     estado: 'cancelada',  clase: 'btn-cancelar' },
      ];
    }
    if (estado === 'en_camino') {
      return [
        { label: '✅ Marcar completado', estado: 'completada', clase: 'btn-completar' },
        { label: '❌ Cancelar',          estado: 'cancelada',  clase: 'btn-cancelar' },
      ];
    }
    return [];
  }
}
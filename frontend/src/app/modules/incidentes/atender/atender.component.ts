import { Component, OnInit, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { IncidenteService, Incidente, AceptarPayload } from '../../../core/services/incidente.service';

@Component({
  selector: 'app-atender-incidente',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './atender.component.html',
  styleUrl: './atender.component.css'
})
export class AtenderComponent implements OnInit {

  incidentes: Incidente[]  = [];
  misCasos:   Incidente[]  = [];
  tabActiva   = 'pendientes';

  // Modal de aceptación
  modalAbierto  = false;
  incidenteSeleccionado: Incidente | null = null;
  precio        = 100;
  tiempoMin     = 30;
  notaTaller    = '';

  cargando      = false;
  aceptando     = false;
  error         = '';
  exito         = '';

  constructor(
    private incidenteService: IncidenteService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit() { this.cargar(); }

  cargar() {
    this.cargando = true;
    this.error    = '';
    this.incidenteService.getDisponibles().subscribe({
      next: data => {
        this.ngZone.run(() => {
          this.incidentes = data;
          this.cargando   = false;
          this.cdr.detectChanges();
        });
      },
      error: err => {
        this.ngZone.run(() => {
          this.error    = err.error?.detail || 'Error al cargar incidentes';
          this.cargando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  abrirModal(inc: Incidente) {
    this.incidenteSeleccionado = inc;
    this.precio     = 100;
    this.tiempoMin  = 30;
    this.notaTaller = '';
    this.error      = '';
    this.modalAbierto = true;
    this.cdr.detectChanges();
  }

  cerrarModal() {
    this.modalAbierto          = false;
    this.incidenteSeleccionado = null;
    this.cdr.detectChanges();
  }

  async confirmarAceptacion() {
    if (!this.incidenteSeleccionado) return;
    if (this.precio <= 0) { this.error = 'El precio debe ser mayor a 0'; return; }
    if (this.tiempoMin <= 0) { this.error = 'El tiempo estimado debe ser mayor a 0'; return; }

    this.aceptando = true;
    this.error     = '';

    const usuario  = JSON.parse(localStorage.getItem('usuario') || '{}');

    const payload: AceptarPayload = {
      incidente_id:       this.incidenteSeleccionado.id,
      taller_id:          usuario.id,
      precio_cotizado:    this.precio,
      tiempo_estimado_min: this.tiempoMin,
      nota_taller:        this.notaTaller || undefined,
    };

    try {
      await firstValueFrom(this.incidenteService.aceptarIncidente(payload));
      this.ngZone.run(() => {
        this.exito        = 'Caso aceptado correctamente ✓';
        this.modalAbierto = false;
        this.incidenteSeleccionado = null;
        this.aceptando    = false;
        this.incidentes   = this.incidentes.filter(i => i.id !== payload.incidente_id);
        this.cdr.detectChanges();
      });
      setTimeout(() => this.ngZone.run(() => {
        this.exito = '';
        this.cdr.detectChanges();
      }), 2500);
    } catch (err: any) {
      this.ngZone.run(() => {
        this.error     = err.error?.detail || 'Error al aceptar el caso';
        this.aceptando = false;
        this.cdr.detectChanges();
      });
    }
  }

  setTab(tab: string) {
    this.tabActiva = tab;
    this.cdr.detectChanges();
  }

  formatFecha(fecha: string): string {
    const diff = Date.now() - new Date(fecha).getTime();
    const min  = Math.floor(diff / 60000);
    if (min < 60)   return `Hace ${min} min`;
    const hrs = Math.floor(min / 60);
    if (hrs < 24)   return `Hace ${hrs}h`;
    return new Date(fecha).toLocaleDateString('es-BO');
  }

  get totalDisponibles() { return this.incidentes.length; }
}
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IncidenteService } from '../../../core/services/incidente.service';

@Component({
  selector: 'app-atender-incidente',
  standalone: true,
  imports: [CommonModule],
   templateUrl: './atender.component.html',
  styleUrls: ['./atender.component.css']
})
export class AtenderComponent implements OnInit {
  incidentes: any[] = [];

  constructor(private incidenteService: IncidenteService) {}

  ngOnInit() {
    this.cargarPendientes();
  }

  cargarPendientes() {
    this.incidenteService.getIncidentesPendientes().subscribe(data => this.incidentes = data);
  }

  aceptarCaso(incidenteId: string) {
    const asignacion = {
      incidente_id: incidenteId,
      taller_id: 'TU_ID_DE_TALLER_AQUI', // Debe venir del perfil del técnico/taller logueado
      precio_cotizado: 100.0,
      tiempo_estimado_min: 30
    };

    this.incidenteService.aceptarIncidente(asignacion).subscribe({
      next: () => {
        alert('Has tomado el caso. ¡En camino!');
        this.cargarPendientes();
      }
    });
  }
}
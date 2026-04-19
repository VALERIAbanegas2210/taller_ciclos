import { Component, OnInit, AfterViewInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IncidenteService } from '../../../core/services/incidente.service';
import { VehiculoService } from '../../vehiculos/vehiculo.service';
import * as L from 'leaflet';

@Component({
  selector: 'app-reportar-incidente', // Mantengo tu selector con la 'i' extra
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './reportar.component.html',
  styleUrls: ['./reportar.component.css']
})
export class ReportarComponent implements OnInit, AfterViewInit {
  incidenteForm: FormGroup;
  misVehiculos: any[] = [];
  cargando: boolean = false;

  // Variables para el Mapa
  private map: any;
  private marker: any;
  private defaultIcon = L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  });

  constructor(
    private fb: FormBuilder,
    private incidenteService: IncidenteService,
    private vehiculoService: VehiculoService
  ) {
    this.incidenteForm = this.fb.group({
      vehiculo_id: ['', Validators.required],
      categoria: ['motor', Validators.required],
      direccion_texto: ['', [Validators.required, Validators.minLength(5)]],
      descripcion_manual: ['', [Validators.required, Validators.maxLength(500)]],
      ubicacion: ['0,0'], 
      prioridad: ['media']
    });
  }

  ngOnInit(): void {
    this.cargarVehiculos();
  }

  ngAfterViewInit(): void {
    this.initMap();
  }

  cargarVehiculos(): void {
    this.vehiculoService.getMisVehiculos().subscribe({
      next: (data) => this.misVehiculos = data,
      error: (err) => console.error('Error al cargar vehículos:', err)
    });
  }

  private initMap(): void {
    // Santa Cruz, Bolivia por defecto
    const lat = -17.7833;
    const lng = -63.1821;

    this.map = L.map('map').setView([lat, lng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    this.marker = L.marker([lat, lng], {
      icon: this.defaultIcon,
      draggable: true
    }).addTo(this.map);

    // Al arrastrar manualmente la flecha
    this.marker.on('dragend', () => {
      const position = this.marker.getLatLng();
      this.actualizarUbicacionForm(position.lat, position.lng);
    });

    // Intentar geolocalización automática
    this.map.locate({ setView: true, maxZoom: 16 });
    this.map.on('locationfound', (e: any) => {
      this.marker.setLatLng(e.latlng);
      this.actualizarUbicacionForm(e.latlng.lat, e.latlng.lng);
    });
  }

  actualizarUbicacionForm(lat: number, lng: number) {
    this.incidenteForm.patchValue({
      ubicacion: `${lat},${lng}`
    });
  }

  enviarIncidente(): void {
    if (this.incidenteForm.valid) {
      this.cargando = true;
      this.incidenteService.crearIncidente(this.incidenteForm.value).subscribe({
        next: (res) => {
          alert('¡Incidente reportado con éxito!');
          this.incidenteForm.reset({
            categoria: 'motor',
            ubicacion: '0,0',
            prioridad: 'media'
          });
          this.cargando = false;
        },
        error: (err) => {
          this.cargando = false;
          console.error('Error al guardar:', err);
          alert('Error al reportar: Revisa la conexión o los campos.');
        }
      });
    } else {
      Object.values(this.incidenteForm.controls).forEach(control => control.markAsTouched());
    }
  }
}
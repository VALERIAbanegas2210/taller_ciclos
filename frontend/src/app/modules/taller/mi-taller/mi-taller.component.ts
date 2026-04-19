import { Component, OnInit, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { TallerService, Taller, TallerCreate, TallerUpdate } from '../taller.service';

@Component({
  selector: 'app-mi-taller',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './mi-taller.html',
  styleUrls: ['./mi-taller.css']
})
export class MiTallerComponent implements OnInit {

  taller: Taller | null = null;
  modoRegistro = false;

  // Form registro
  regForm: TallerCreate = this.regVacio();

  // Form edición
  editForm: TallerUpdate = {};

  logoFile: File | null = null;
  logoPreview: string | null = null;

  cargando = false;
  error    = '';
  exito    = '';

  constructor(
    private tallerService: TallerService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    this.cargarTaller();
  }

  cargarTaller() {
    const tallerId = localStorage.getItem('taller_id');
    if (!tallerId) {
      this.modoRegistro = true;
      this.cdr.detectChanges();
      return;
    }
    this.tallerService.obtener(tallerId).subscribe({
      next: t => {
        this.taller      = t;
        this.logoPreview = t.logo_url;
        this.sincEditForm(t);
        this.cdr.detectChanges();
      },
      error: () => {
        this.modoRegistro = true;
        this.cdr.detectChanges();
      }
    });
  }

  sincEditForm(t: Taller) {
    this.editForm = {
      nombre:            t.nombre,
      telefono:          t.telefono || '',
      direccion:         t.direccion || '',
      radio_servicio_km: t.radio_servicio_km || 10,
      descripcion:       t.descripcion || '',
    };
  }

  regVacio(): TallerCreate {
    return {
      nombre: '', email: '', password: '',
      telefono: '', direccion: '', descripcion: '',
      radio_servicio_km: 10, latitud: null, longitud: null
    };
  }

  handleLogo(event: any) {
    const file: File = event.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { this.error = 'El logo supera 5 MB'; return; }
    this.logoFile = file;
    const reader  = new FileReader();
    reader.onload = () => {
      this.logoPreview = reader.result as string;
      this.cdr.detectChanges();
    };
    reader.readAsDataURL(file);
  }

  async registrar() {
    this.error = '';
    this.exito = '';

    if (!this.regForm.nombre.trim() || !this.regForm.email.trim() || !this.regForm.password.trim()) {
      this.error = 'Nombre, email y contraseña son obligatorios';
      return;
    }
    if (this.regForm.password.length < 8) {
      this.error = 'La contraseña debe tener al menos 8 caracteres';
      return;
    }

    this.cargando = true;
    this.cdr.detectChanges();

    try {
      const taller = await firstValueFrom(this.tallerService.registrar(this.regForm));

      // Subir logo si hay uno
      if (this.logoFile && taller.id) {
        await this.subirLogoFetch(taller.id);
      }

      localStorage.setItem('taller_id', taller.id);

      this.ngZone.run(() => {
        this.taller       = taller;
        this.modoRegistro = false;
        this.sincEditForm(taller);
        this.exito    = 'Taller registrado correctamente ✓';
        this.cargando = false;
        this.cdr.detectChanges();
      });

    } catch (err: any) {
      this.ngZone.run(() => {
        this.error    = err.error?.detail || 'Error al registrar el taller';
        this.cargando = false;
        this.cdr.detectChanges();
      });
    }
  }

  async guardar() {
    this.error = '';
    this.exito = '';

    if (!this.taller) return;
    if (!this.editForm.nombre?.trim()) {
      this.error = 'El nombre no puede estar vacío';
      return;
    }

    this.cargando = true;
    this.cdr.detectChanges();

    try {
      const actualizado = await firstValueFrom(
        this.tallerService.actualizar(this.taller.id, this.editForm)
      );

      if (this.logoFile && actualizado.id) {
        await this.subirLogoFetch(actualizado.id);
        actualizado.logo_url = this.logoPreview;
      }

      this.ngZone.run(() => {
        this.taller   = { ...actualizado };
        this.logoFile = null;
        this.exito    = 'Cambios guardados correctamente ✓';
        this.cargando = false;
        this.cdr.detectChanges();
      });

      setTimeout(() => this.ngZone.run(() => {
        this.exito = '';
        this.cdr.detectChanges();
      }), 2500);

    } catch (err: any) {
      this.ngZone.run(() => {
        this.error    = err.error?.detail || 'Error al guardar los cambios';
        this.cargando = false;
        this.cdr.detectChanges();
      });
    }
  }

  private async subirLogoFetch(tallerId: string) {
    if (!this.logoFile) return;
    try {
      const token    = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('logo', this.logoFile, this.logoFile.name);
      const res = await fetch(
        `http://localhost:8000/api/talleres/mi-taller/${tallerId}/logo`,
        { method: 'POST', headers: { 'Authorization': `Bearer ${token}` }, body: formData }
      );
      if (res.ok) {
        const data       = await res.json();
        if (this.taller) this.taller.logo_url = data.logo_url;
        this.logoPreview = data.logo_url;
      }
    } catch (e) {
      console.warn('Error subiendo logo:', e);
    } finally {
      this.logoFile = null;
    }
  }

  cancelar() {
    if (this.taller) this.sincEditForm(this.taller);
    this.error       = '';
    this.exito       = '';
    this.logoFile    = null;
    this.logoPreview = this.taller?.logo_url || null;
    this.cdr.detectChanges();
  }

  get iniciales(): string {
    return this.taller?.nombre?.slice(0, 2).toUpperCase() || 'TL';
  }
}
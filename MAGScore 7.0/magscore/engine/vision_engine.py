"""
MAGScore 7.0 — Vision Engine v1
================================
Traitement de flux vidéo et extraction de signaux visuels.

Approche V1 (Simple) :
    - Heuristiques légères (densité, mouvement global)
    - Pas de CNN/modèle lourd
    - numpy + cv2 pour calculs matriciels simples

Types de flux pris en charge :
    - HLS, MP4 via API Football Pro ou tiers
    - Résolution minimale : 1280×720 (HD)
    - Fréquence : 25-30 ips (down-sampling accepté)

Vision : NO CHANCE — ONLY PATTERNS
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None

from .definitions import (
    Frame,
    VisualSignal,
    discretize_visual_signal,
    VISUAL_THRESHOLDS,
)


# =============================================================================
# VERSION
# =============================================================================

VISION_ENGINE_VERSION = "1.0"


# =============================================================================
# EXCEPTIONS
# =============================================================================

class VisionEngineError(Exception):
    """Exception levée par le VisionEngine."""
    pass


class VideoStreamError(VisionEngineError):
    """Exception levée lors d'erreurs de flux vidéo."""
    pass


class FrameProcessingError(VisionEngineError):
    """Exception levée lors du traitement d'une frame."""
    pass


# =============================================================================
# VIDEO STREAM HANDLER
# =============================================================================

class VideoStreamHandler:
    """
    Gestionnaire de flux vidéo pour l'extraction de frames.
    
    Gère l'ouverture, la lecture et la fermeture des flux vidéo.
    Supporte HLS, MP4 et autres formats via cv2.VideoCapture.
    
    Note V1: Implémentation simple sans streaming avancé.
    """
    
    def __init__(self, source: Optional[str] = None) -> None:
        """
        Initialise le gestionnaire de flux.
        
        Args:
            source: URL ou chemin du flux vidéo (optionnel).
        """
        self._source = source
        self._capture = None
        self._is_open = False
        self._frame_count = 0
        self._fps = 0.0
        self._width = 0
        self._height = 0
        self._logger = logging.getLogger(__name__)
    
    @property
    def is_available(self) -> bool:
        """Vérifie si cv2 est disponible."""
        return HAS_CV2
    
    @property
    def is_open(self) -> bool:
        """Vérifie si le flux est ouvert."""
        return self._is_open
    
    @property
    def fps(self) -> float:
        """Retourne le FPS du flux."""
        return self._fps
    
    @property
    def resolution(self) -> Tuple[int, int]:
        """Retourne la résolution (width, height)."""
        return (self._width, self._height)
    
    def open(self, source: str) -> bool:
        """
        Ouvre un flux vidéo.
        
        Args:
            source: URL ou chemin du flux.
        
        Returns:
            True si l'ouverture a réussi.
        
        Raises:
            VideoStreamError: Si cv2 n'est pas disponible ou ouverture échoue.
        """
        if not HAS_CV2:
            raise VideoStreamError("OpenCV (cv2) n'est pas installé")
        
        try:
            self._capture = cv2.VideoCapture(source)
            
            if not self._capture.isOpened():
                raise VideoStreamError(f"Impossible d'ouvrir le flux : {source}")
            
            self._source = source
            self._is_open = True
            self._fps = self._capture.get(cv2.CAP_PROP_FPS)
            self._width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self._frame_count = int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self._logger.info(
                f"Flux ouvert: {source} ({self._width}x{self._height} @ {self._fps}fps)"
            )
            
            return True
            
        except Exception as e:
            raise VideoStreamError(f"Erreur d'ouverture du flux: {str(e)}") from e
    
    def read_frame(self) -> Optional[Any]:
        """
        Lit la prochaine frame du flux.
        
        Returns:
            Frame numpy array ou None si fin du flux.
        """
        if not self._is_open or self._capture is None:
            return None
        
        ret, frame = self._capture.read()
        
        if not ret:
            return None
        
        return frame
    
    def close(self) -> None:
        """Ferme le flux vidéo."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        
        self._is_open = False
        self._logger.info("Flux vidéo fermé")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# =============================================================================
# VISION SIGNAL EXTRACTOR
# =============================================================================

class VisionSignalExtractor:
    """
    Extracteur de signaux visuels à partir de frames vidéo.
    
    Approche V1 :
        - Analyse de densité de pixels (zones défensives/offensives)
        - Calcul de flux optique simplifié (mouvement global)
        - Détection de clusters de joueurs (blobs)
    
    Les signaux extraits sont ensuite discrétisés pour le PatternEngine.
    """
    
    def __init__(self) -> None:
        """Initialise l'extracteur de signaux visuels."""
        self._logger = logging.getLogger(__name__)
        self._prev_frame = None
    
    @property
    def is_available(self) -> bool:
        """Vérifie si numpy et cv2 sont disponibles."""
        return HAS_NUMPY and HAS_CV2
    
    def extract_metrics(self, frame: Any) -> Dict[str, float]:
        """
        Extrait les métriques brutes d'une frame.
        
        Args:
            frame: Frame numpy array (BGR).
        
        Returns:
            Dict des métriques extraites :
            {
                "density_def": float,      # Densité zone défensive
                "density_off": float,      # Densité zone offensive
                "optical_flow_avg": float, # Mouvement global moyen
                "cluster_density": float,  # Densité de clusters
            }
        """
        if not self.is_available:
            return self._fallback_metrics()
        
        if frame is None:
            return self._fallback_metrics()
        
        try:
            metrics = {}
            
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Zone défensive (tiers inférieur)
            def_zone = gray[int(height * 0.66):, :]
            metrics["density_def"] = self._compute_density(def_zone)
            
            # Zone offensive (tiers supérieur)
            off_zone = gray[:int(height * 0.33), :]
            metrics["density_off"] = self._compute_density(off_zone)
            
            # Flux optique (mouvement global)
            metrics["optical_flow_avg"] = self._compute_optical_flow(gray)
            
            # Densité de clusters (blobs)
            metrics["cluster_density"] = self._compute_cluster_density(gray)
            
            # Sauvegarder pour le prochain calcul de flux optique
            self._prev_frame = gray.copy()
            
            return metrics
            
        except Exception as e:
            self._logger.warning(f"Erreur extraction métriques: {e}")
            return self._fallback_metrics()
    
    def _compute_density(self, zone: Any) -> float:
        """
        Calcule la densité de pixels actifs dans une zone.
        
        Args:
            zone: Zone de l'image (numpy array grayscale).
        
        Returns:
            Valeur entre 0.0 et 1.0.
        """
        if zone is None or zone.size == 0:
            return 0.5
        
        # Seuillage simple pour détecter les pixels "actifs"
        # (joueurs, ballon, lignes = pixels clairs ou très foncés)
        _, binary = cv2.threshold(zone, 127, 255, cv2.THRESH_BINARY)
        
        # Compter les pixels blancs
        white_pixels = np.sum(binary == 255)
        total_pixels = binary.size
        
        density = white_pixels / total_pixels if total_pixels > 0 else 0.5
        
        return min(1.0, max(0.0, density))
    
    def _compute_optical_flow(self, gray: Any) -> float:
        """
        Calcule le flux optique simplifié (mouvement global).
        
        Args:
            gray: Frame en niveaux de gris.
        
        Returns:
            Valeur entre 0.0 et 1.0 indiquant l'intensité du mouvement.
        """
        if self._prev_frame is None:
            return 0.5
        
        try:
            # Différence absolue entre frames
            diff = cv2.absdiff(gray, self._prev_frame)
            
            # Moyenne de la différence
            mean_diff = np.mean(diff) / 255.0
            
            # Normaliser entre 0 et 1
            return min(1.0, max(0.0, mean_diff * 5))  # Facteur d'amplification
            
        except Exception:
            return 0.5
    
    def _compute_cluster_density(self, gray: Any) -> float:
        """
        Calcule la densité de clusters (groupes de joueurs).
        
        Approche V1 simple : utilise le nombre de contours détectés.
        
        Args:
            gray: Frame en niveaux de gris.
        
        Returns:
            Valeur entre 0.0 et 1.0.
        """
        try:
            # Flouter pour réduire le bruit
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Seuillage adaptatif
            _, binary = cv2.threshold(
                blurred, 0, 255, 
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            
            # Trouver les contours
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filtrer les petits contours (bruit)
            min_area = gray.size * 0.001  # 0.1% de l'image
            valid_contours = [
                c for c in contours 
                if cv2.contourArea(c) > min_area
            ]
            
            # Normaliser le nombre de clusters (max ~22 joueurs visibles)
            cluster_count = len(valid_contours)
            normalized = min(1.0, cluster_count / 25.0)
            
            return normalized
            
        except Exception:
            return 0.5
    
    def _fallback_metrics(self) -> Dict[str, float]:
        """Retourne des métriques par défaut si extraction impossible."""
        return {
            "density_def": 0.5,
            "density_off": 0.5,
            "optical_flow_avg": 0.5,
            "cluster_density": 0.5,
        }
    
    def discretize_signals(
        self, 
        raw_signals: Dict[str, float]
    ) -> VisualSignal:
        """
        Convertit les signaux bruts en codes discrets pour le PatternEngine.
        
        Args:
            raw_signals: Dict des métriques brutes (valeurs 0.0-1.0).
        
        Returns:
            VisualSignal avec raw et discrete.
        """
        discrete: List[str] = []
        
        # Mapper chaque métrique vers un code discret
        if "density_def" in raw_signals:
            code = discretize_visual_signal(
                raw_signals["density_def"], "VIS_DEF"
            )
            discrete.append(code)
        
        if "density_off" in raw_signals:
            code = discretize_visual_signal(
                raw_signals["density_off"], "VIS_OFF"
            )
            discrete.append(code)
        
        if "optical_flow_avg" in raw_signals:
            code = discretize_visual_signal(
                raw_signals["optical_flow_avg"], "VIS_FLOW"
            )
            discrete.append(code)
        
        if "cluster_density" in raw_signals:
            code = discretize_visual_signal(
                raw_signals["cluster_density"], "VIS_CLUSTER"
            )
            discrete.append(code)
        
        return VisualSignal(raw=raw_signals, discrete=discrete)


# =============================================================================
# VISION ENGINE
# =============================================================================

class VisionEngine:
    """
    Moteur de vision principal MAGScore 7.0.
    
    Orchestre le traitement de flux vidéo :
        1. Ouvre le flux via VideoStreamHandler
        2. Échantillonne les frames
        3. Extrait les métriques via VisionSignalExtractor
        4. Discrétise les signaux pour le PatternEngine
    
    Note V1: Traitement simplifié, heuristiques légères.
    """
    
    def __init__(self) -> None:
        """Initialise le Vision Engine."""
        self._stream_handler = VideoStreamHandler()
        self._signal_extractor = VisionSignalExtractor()
        self._version = VISION_ENGINE_VERSION
        self._logger = logging.getLogger(__name__)
    
    @property
    def version(self) -> str:
        """Retourne la version du Vision Engine."""
        return self._version
    
    @property
    def is_available(self) -> bool:
        """Vérifie si le traitement vidéo est disponible."""
        return HAS_NUMPY and HAS_CV2
    
    def process_stream(
        self, 
        video_url: str,
        sample_interval: int = 30
    ) -> List[Frame]:
        """
        Traite un flux vidéo et extrait les frames échantillonnées.
        
        Args:
            video_url: URL ou chemin du flux vidéo.
            sample_interval: Intervalle d'échantillonnage (nombre de frames).
        
        Returns:
            Liste des Frame avec métriques.
        
        Raises:
            VideoStreamError: Si le flux ne peut être ouvert.
        """
        if not self.is_available:
            self._logger.warning("Vision Engine non disponible (numpy/cv2 manquant)")
            return []
        
        frames: List[Frame] = []
        
        try:
            self._stream_handler.open(video_url)
            
            frame_idx = 0
            while True:
                raw_frame = self._stream_handler.read_frame()
                
                if raw_frame is None:
                    break
                
                # Échantillonner selon l'intervalle
                if frame_idx % sample_interval == 0:
                    metrics = self._signal_extractor.extract_metrics(raw_frame)
                    
                    # Calculer le timestamp approximatif
                    fps = self._stream_handler.fps or 25.0
                    timestamp = datetime.now()  # En prod: calculer depuis le début
                    
                    frames.append(Frame(
                        timestamp=timestamp,
                        metrics=metrics
                    ))
                
                frame_idx += 1
            
            self._logger.info(f"Traité {frame_idx} frames, {len(frames)} échantillons")
            
        except VideoStreamError:
            raise
        except Exception as e:
            self._logger.error(f"Erreur traitement flux: {e}")
        finally:
            self._stream_handler.close()
        
        return frames
    
    def extract_signals(self, frames: List[Frame]) -> Dict[str, float]:
        """
        Agrège les métriques de plusieurs frames en signaux moyens.
        
        Args:
            frames: Liste des Frame avec métriques.
        
        Returns:
            Dict des signaux agrégés.
        """
        if not frames:
            return self._signal_extractor._fallback_metrics()
        
        # Initialiser les accumulateurs
        aggregated: Dict[str, List[float]] = {}
        
        for frame in frames:
            for key, value in frame.metrics.items():
                if key not in aggregated:
                    aggregated[key] = []
                aggregated[key].append(value)
        
        # Calculer les moyennes
        result: Dict[str, float] = {}
        for key, values in aggregated.items():
            result[key] = sum(values) / len(values) if values else 0.5
        
        return result
    
    def discretize(
        self, 
        raw_signals: Dict[str, float]
    ) -> List[str]:
        """
        Discrétise les signaux bruts en codes pour le PatternEngine.
        
        Args:
            raw_signals: Signaux bruts (valeurs 0.0-1.0).
        
        Returns:
            Liste des codes discrets.
        """
        visual_signal = self._signal_extractor.discretize_signals(raw_signals)
        return visual_signal.discrete
    
    def process_and_discretize(
        self, 
        video_url: str,
        sample_interval: int = 30
    ) -> VisualSignal:
        """
        Pipeline complet : traite le flux et retourne les signaux discrétisés.
        
        Args:
            video_url: URL ou chemin du flux vidéo.
            sample_interval: Intervalle d'échantillonnage.
        
        Returns:
            VisualSignal avec raw et discrete.
        """
        if not self.is_available:
            return VisualSignal(
                raw=self._signal_extractor._fallback_metrics(),
                discrete=["VIS_DEF_MED", "VIS_OFF_MED", "VIS_FLOW_MED", "VIS_CLUSTER_MED"]
            )
        
        frames = self.process_stream(video_url, sample_interval)
        raw_signals = self.extract_signals(frames)
        
        return self._signal_extractor.discretize_signals(raw_signals)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_vision_engine() -> VisionEngine:
    """
    Factory function pour créer un VisionEngine.
    
    Returns:
        Instance de VisionEngine.
    """
    return VisionEngine()


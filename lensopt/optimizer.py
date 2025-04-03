# optimized_optimizer.py
from tqdm import tqdm

class OpticalSystemOptimizer:
    """
    Unified optical system optimizer that handles 2-4 lenses with configurable settings.
    """
    def __init__(self, zosapi, the_system, lens_count=3, rms_threshold=300, 
                 aperture=10, num_cores=8, max_iterations=30, ap_position=1, is_macro=False):
        self.ZOSAPI = zosapi
        self.TheSystem = the_system
        self.lens_count = lens_count
        self.rms_threshold = rms_threshold
        self.aperture = aperture
        self.num_cores = num_cores
        self.max_iterations = max_iterations
        self.ap_position = ap_position
        self.is_macro = is_macro
        
        # Standard distances
        self.DEFAULT_SPACING = 2.0
        self.DEFAULT_IMAGE_DISTANCE = 200.0
        self.DEFAULT_OBJECT_DISTANCE = 150.0

    def optimize_lens_combinations(self, lens_combinations, type_code=1):
        """Optimize lens combinations based on the configured parameters."""
        desc = f"Optimizing {self.lens_count}-lens combinations"
        for comb in tqdm(lens_combinations, desc=desc, unit="combination", 
                       miniters=len(lens_combinations), ncols=100):
            try:
                # Skip combinations that don't meet focal length criteria (except for macro systems)
                if not self.is_macro and not self._check_focal_length(comb):
                    continue
                    
                # Reset system and prepare surfaces
                self._initialize_system()
                
                # Configure system
                self._configure_aperture_and_field(type_code)
                
                # Setup system with appropriate number of surfaces
                self._setup_system_layout()
                
                # Configure lens parameters
                self._configure_lens_parameters(comb)
                
                # Optimize system and evaluate results
                self._optimize_system()
                weighted_rms = self._evaluate_results()
                
                if weighted_rms < self.rms_threshold:
                    print(f"{self.lens_count}-lens combination: {comb}, Weighted RMS: {weighted_rms}")
                    
            except Exception as e:
                print(f"Error processing combination {comb}: {e}")
    
    def _initialize_system(self):
        """Initialize optical system."""
        self.TheSystem.New(True)
        self.TheLDE = self.TheSystem.LDE
        self.TheSystemData = self.TheSystem.SystemData

    def _setup_system_layout(self):
        """Set up system layout based on lens count and aperture position."""
        # Calculate surfaces needed (2 surfaces per lens)
        total_surfaces = self.lens_count * 2
        stop_surface_index = 1  # Default stop position
        
        if self.ap_position == 0:
            # All surfaces after stop
            for _ in range(total_surfaces):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
                
        elif self.ap_position == 1:
            # First lens before stop, remaining after
            surfaces_before = 2
            surfaces_after = total_surfaces - surfaces_before
            
            # Insert surfaces before stop
            for _ in range(surfaces_before):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
            
            # Update stop index after insertions
            stop_surface_index += surfaces_before
            
            # Insert surfaces after stop
            for _ in range(surfaces_after):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
                
        elif self.ap_position == 2:
            # Two lenses before stop, remaining after
            surfaces_before = 4
            surfaces_after = total_surfaces - surfaces_before
            
            # Insert surfaces before stop
            for _ in range(surfaces_before):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
            
            # Update stop index after insertions
            stop_surface_index += surfaces_before
            
            # Insert surfaces after stop
            for _ in range(surfaces_after):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
                
        elif self.ap_position == 3:
            # Three lenses before stop, remaining after
            surfaces_before = 6
            surfaces_after = total_surfaces - surfaces_before
            
            # Insert surfaces before stop
            for _ in range(surfaces_before):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
            
            # Update stop index after insertions
            stop_surface_index += surfaces_before
            
            # Insert remaining surfaces after stop
            for _ in range(surfaces_after):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
                
        elif self.ap_position == 4:
            # All surfaces before stop
            for _ in range(total_surfaces):
                self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
                
        # Retrieve surface objects
        self._retrieve_surfaces(total_surfaces + 1)

    def _retrieve_surfaces(self, count):
        """Helper to retrieve surface objects."""
        for i in range(2*count+1):
            surf = self.TheLDE.GetSurfaceAt(i)
            if surf is not None:
                setattr(self, f"Surface_{i}", surf)
            setattr(self, f"Surface_{i}", self.TheLDE.GetSurfaceAt(i))
    
    def _configure_lens_parameters(self, comb):
        """Configure lens parameters based on lens count and aperture position."""
        # Calculate lens arrangement
        lenses_before_stop = min(self.ap_position, self.lens_count)
        lenses_after_stop = self.lens_count - lenses_before_stop
        
        # Object surface
        if self.is_macro:
            self.Surface_0.Thickness = self.DEFAULT_OBJECT_DISTANCE
            self.Surface_0.ThicknessCell.MakeSolveVariable()
        
        # Configure first surface
        first_surface_idx = 1
        if lenses_before_stop == 0:
            # First lens after stop
            first_surface_idx = 2
            self.Surface_1.Thickness = self.DEFAULT_SPACING
            self.Surface_1.ThicknessCell.MakeSolveVariable()
        
        # Configure lenses before stop
        surface_idx = first_surface_idx
        for i in range(lenses_before_stop):
            # Configure lens
            self._configure_single_lens(surface_idx, comb[i])
            # Make thickness variable
            surf = getattr(self, f"Surface_{surface_idx + 1}")  # Changed from Surface_surface_
            surf.ThicknessCell.MakeSolveVariable()
            surface_idx += 2
        
        # Configure stop if needed
        if lenses_before_stop > 0 and lenses_after_stop > 0:
            # Stop is between lenses
            surf = getattr(self, f"Surface_{surface_idx}")  # Changed from Surface_surface_
            surf.Thickness = self.DEFAULT_SPACING
            surf.ThicknessCell.MakeSolveVariable()
            surface_idx += 1
        
        # Configure lenses after stop
        for i in range(lenses_before_stop, self.lens_count):
            # Configure lens
            self._configure_single_lens(surface_idx, comb[i])
            # Make thickness variable (except last surface)
            if i < self.lens_count - 1:
                surf = getattr(self, f"Surface_{surface_idx + 1}")  # Changed from Surface_surface_
                surf.ThicknessCell.MakeSolveVariable()
            surface_idx += 2
        
        # Set image distance
        last_surface = getattr(self, f"Surface_{surface_idx - 1}")
        last_surface.Thickness = self.DEFAULT_IMAGE_DISTANCE
        last_surface.ThicknessCell.MakeSolveVariable()
    
    def _configure_single_lens(self, surface_idx, lens_data):
        """Configure a single lens using lens data."""
        front_surface = getattr(self, f"Surface_{surface_idx}")
        back_surface = getattr(self, f"Surface_{surface_idx + 1}")
        
        # Set common parameters for both surfaces
        front_surface.SemiDiameter = back_surface.SemiDiameter = 0.5 * lens_data[1]
        
        # Configure front surface
        front_surface.Radius = lens_data[2]
        front_surface.Thickness = lens_data[4]
        front_surface.Material = lens_data[5]
        
        # Configure back surface
        back_surface.Radius = lens_data[3]
        back_surface.Thickness = self.DEFAULT_SPACING  # Default spacing, will be variable
    
    def _check_focal_length(self, comb):
        """Check if focal length meets criteria."""
        lens_focals = [comb[i][6] for i in range(self.lens_count)]
        effective_f = self._effective_focal_length(lens_focals)
        return 0 < effective_f <= 1500
    
    def _effective_focal_length(self, lens_focals):
        """Calculate effective focal length."""
        # Check for zero focal lengths
        if 0 in lens_focals:
            return float('inf')
            
        # Calculate combined focal length using 1/f = sum(1/f_i)
        if all(f != 0 for f in lens_focals):
            return 1.0 / sum(1.0 / f for f in lens_focals)
        return float('inf')
    
    def _configure_aperture_and_field(self, type_code):
        """Configure aperture and field settings."""
        aperture_mapping = {
            1: self.ZOSAPI.SystemData.ZemaxApertureType.EntrancePupilDiameter,
            2: self.ZOSAPI.SystemData.ZemaxApertureType.ImageSpaceFNum,
            3: self.ZOSAPI.SystemData.ZemaxApertureType.ObjectSpaceNA    
        }
        self.TheSystemData.Aperture.ApertureType = aperture_mapping[type_code]
        self.TheSystemData.Aperture.ApertureValue = self.aperture
        
        # Set field parameters
        fields = self.TheSystem.SystemData.Fields
        fields.SetFieldType(self.ZOSAPI.SystemData.FieldType.RealImageHeight)
        fields.AddField(0, 11, 1)
        fields.AddField(0, 21.6, 1)
        self.TheSystemData.Wavelengths.SelectWavelengthPreset(self.ZOSAPI.SystemData.WavelengthPreset.FdC_Visible)
        
    def _optimize_system(self):
        """Run optimization routines."""
        # Quick focus
        quickFocus = self.TheSystem.Tools.OpenQuickFocus()
        quickFocus.Criterion = self.ZOSAPI.Tools.General.QuickFocusCriterion.SpotSizeRadial
        quickFocus.UseCentroid = True
        quickFocus.RunAndWaitForCompletion()
        quickFocus.Close()
        
        # Optimization wizard
        mfe = self.TheSystem.MFE
        opt_wizard = mfe.SEQOptimizationWizard
        
        opt_wizard.Data = 5
        opt_wizard.OverallWeight = 2
        opt_wizard.Ring = 1
        opt_wizard.IsAirUsed = True
        opt_wizard.AirMin = 0.5
        opt_wizard.AirMax = 1000.0
        opt_wizard.AirEdge = 1
        opt_wizard.Apply()
        
        # Local optimization
        local_opt = self.TheSystem.Tools.OpenLocalOptimization()
        local_opt.Algorithm = self.ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares
        local_opt.Cycles = self.ZOSAPI.Tools.Optimization.OptimizationCycles.Automatic
        local_opt.MaximumIterations = self.max_iterations
        local_opt.TerminateOnConvergence = True
        local_opt.NumberOfCores = self.num_cores
        local_opt.RunAndWaitForCompletion()
        local_opt.Close()

    def _evaluate_results(self):
        """Evaluate optimization results."""
        # Open Spot Diagram analysis
        spot = self.TheSystem.Analyses.New_StandardSpot()
        spot.ApplyAndWaitForCompletion()
        spot_results = spot.GetResults()
        
        # Extract RMS radii
        rms_values = [
            spot_results.SpotData.GetRMSSpotSizeFor(i, 1) for i in range(1, 4)
        ]
        
        # Check for valid RMS values
        if 0 in rms_values:
            return float('inf')
        
        # Calculate weighted RMS (more weight to first wavelength)
        weighted_rms = sum((2.5 - i) * rms for i, rms in enumerate(rms_values))
        return weighted_rms
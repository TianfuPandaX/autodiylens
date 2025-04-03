from tqdm import tqdm

class OpticalSystemOptimizer:
    def __init__(self, zosapi, the_system, rms_threshold=300, aperture=10, num_cores=8, max_iterations=30, ap=1):
        self.ZOSAPI = zosapi
        self.TheSystem = the_system
        self.rms_threshold = rms_threshold
        self.Aperture = aperture
        self.num_cores = num_cores
        self.max_iterations = max_iterations
        self.ap = ap

    def optimize_lens_combinations(self, lens_combinations, type_code=1):
        for comb in tqdm(lens_combinations, desc="Optimizing combinations", unit="combination", 
                        miniters=len(lens_combinations), ncols=100):
            try:
                # Check focal length criteria
                if not self._check_focal_length(comb):
                    continue
                    
                # Reset system and prepare surfaces
                self._initialize_system()
                
                # Configure system
                self._configure_aperture_and_field(type_code)
                self._configure_lens_parameters_dispatcher(comb)
                
                # Optimize system and evaluate results
                self._optimize_system()
                weighted_rms = self._evaluate_results()
                
                if weighted_rms < self.rms_threshold:
                    print(f"组合：{comb}, 权重 RMS: {weighted_rms}")
                    
            except Exception as e:
                print(f"Error processing combination {comb}: {e}")
    
    def _initialize_system(self):
        """Initialize optical system"""
        self.TheSystem.New(True)
        self.TheLDE = self.TheSystem.LDE
        self.TheSystemData = self.TheSystem.SystemData

    def _configure_lens_parameters_dispatcher(self, comb):
        """Dispatch to appropriate lens configuration method"""
        layout_method = getattr(self, f"_setup_system_layout{self.ap}")
        layout_method()
        
        config_method = getattr(self, f"_configure_lens_parameters_{self.ap}")
        config_method(comb)
        
    def _setup_system_layout0(self):
        """Setup system layout with surfaces after stop"""
        stop_surface_index = 1
        
        # Insert surfaces after stop surface
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        # Retrieve surface objects
        self._retrieve_surfaces(5)

    def _setup_system_layout1(self):
        """Setup system layout with surfaces around stop"""
        stop_surface_index = 1
        
        # Insert surfaces before stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        # Update stop index
        stop_surface_index += 2
        
        # Insert surfaces after stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        # Retrieve surface objects
        self._retrieve_surfaces(5)

    def _setup_system_layout2(self):
        """Setup system layout with surfaces before stop"""
        stop_surface_index = 1
        
        # Insert surfaces before stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        # Retrieve surface objects
        self._retrieve_surfaces(5)
    
    def _retrieve_surfaces(self, count):
        """Helper to retrieve surface objects"""
        for i in range(1, count + 1):
            setattr(self, f"Surface_{i}", self.TheLDE.GetSurfaceAt(i))
    
    def _configure_lens_parameters_0(self, comb):
        """Configure lens parameters - method 0"""
        # First lens
        self.Surface_2.SemiDiameter = self.Surface_3.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_2.Radius = comb[0][2]
        self.Surface_2.Thickness = comb[0][4]
        self.Surface_2.Material = comb[0][5]
        self.Surface_3.Thickness = 2
        self.Surface_3.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Radius = comb[1][3]
        self.Surface_5.Thickness = 200
        
        self.Surface_1.Thickness = 2
        
        # Set variable parameters
        self.Surface_1.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_1(self, comb):
        """Configure lens parameters - method 1"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Radius = comb[1][3]
        self.Surface_5.Thickness = 200
        
        self.Surface_3.Thickness = 2
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_2(self, comb):
        """Configure lens parameters - method 2"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Radius = comb[1][3]
        self.Surface_4.Thickness = 2
        
        self.Surface_5.Thickness = 200
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()

    def _check_focal_length(self, comb):
        """Check if focal length meets criteria"""
        lens_focals = [comb[0][6], comb[1][6]]
        effective_f = self._effective_focal_length(lens_focals)
        return 0 < effective_f <= 1500
    
    def _effective_focal_length(self, lens_focals):
        """Calculate effective focal length"""
        if all(f != 0 for f in lens_focals):
            return 1.0 / sum(1.0 / f for f in lens_focals)
        return float('inf')
    
    def _configure_aperture_and_field(self, type_code):
        """Configure aperture and field settings"""
        aperture_mapping = {
            1: self.ZOSAPI.SystemData.ZemaxApertureType.EntrancePupilDiameter,
            2: self.ZOSAPI.SystemData.ZemaxApertureType.ImageSpaceFNum,
            3: self.ZOSAPI.SystemData.ZemaxApertureType.ObjectSpaceNA    
        }
        self.TheSystemData.Aperture.ApertureType = aperture_mapping[type_code]
        self.TheSystemData.Aperture.ApertureValue = self.Aperture
        
        # Set field parameters
        fields = self.TheSystem.SystemData.Fields
        fields.SetFieldType(self.ZOSAPI.SystemData.FieldType.RealImageHeight)
        fields.AddField(0, 11, 1)
        fields.AddField(0, 21.6, 1)
        self.TheSystemData.Wavelengths.SelectWavelengthPreset(self.ZOSAPI.SystemData.WavelengthPreset.FdC_Visible)
        
    def _optimize_system(self):
        """Run optimization routines"""
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
        local_opt.NumberOfCores = self.num_cores  # Use the parameter value
        local_opt.RunAndWaitForCompletion()
        local_opt.Close()

    def _evaluate_results(self):
        """Evaluate optimization results"""
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
        
        # Calculate weighted RMS
        weighted_rms = sum((2.5 - i) * rms for i, rms in enumerate(rms_values))
        return weighted_rms

class TripleLensOptimizer(OpticalSystemOptimizer):
    def __init__(self, zosapi, the_system, rms_threshold=300, aperture=10, num_cores=8, max_iterations=30, ap=1):
        super().__init__(zosapi, the_system, rms_threshold, aperture, num_cores,max_iterations, ap )
    
    def optimize_lens_combinations(self, lens_combinations, type_code=1):
        """Optimize triple lens combinations"""
        for comb in tqdm(lens_combinations, desc="Optimizing triple lens combinations", 
                        unit="combination", miniters=len(lens_combinations), ncols=100):
            try:
                # Check focal length criteria
                if not self._check_focal_length(comb):
                    continue
                    
                # Reset system and prepare surfaces
                self._initialize_system()
                
                # Configure system
                self._configure_aperture_and_field(type_code)
                self._configure_lens_parameters_dispatcher(comb)
                
                # Optimize system and evaluate results
                self._optimize_system()
                weighted_rms = self._evaluate_results()
                
                if weighted_rms < self.rms_threshold:
                    print(f"三镜片组合：{comb}, 权重 RMS: {weighted_rms}")
                    
            except Exception as e:
                print(f"Error processing triple lens combination {comb}: {e}")
    
    def _check_focal_length(self, comb):
        """Check if triple lens focal length meets criteria"""
        lens_focals = [comb[0][6], comb[1][6], comb[2][6]]
        effective_f = self._effective_focal_length(lens_focals)
        return 0 < effective_f <= 1500
    
    def _configure_lens_parameters_dispatcher(self, comb):
        """Dispatch to appropriate triple lens configuration method"""
        layout_method = getattr(self, f"_setup_system_layout_triple{self.ap}")
        layout_method()
        
        config_method = getattr(self, f"_configure_lens_parameters_triple{self.ap}")
        config_method(comb)
    
    def _setup_system_layout_triple0(self):
        """Setup triple lens system layout - method 0"""
        stop_surface_index = 1
        
        # Insert 6 surfaces for three lenses
        for _ in range(6):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        # Retrieve surface objects
        self._retrieve_surfaces(7)
    
    def _setup_system_layout_triple1(self):
        """Setup triple lens system layout - method 1"""
        stop_surface_index = 1
        
        # Insert 2 surfaces before stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 2
        
        # Insert 4 surfaces after stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        # Retrieve surface objects
        self._retrieve_surfaces(7)

    def _setup_system_layout_triple2(self):
        """Setup triple lens system layout - method 2"""
        stop_surface_index = 1
        
        # Insert 4 surfaces before stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 4
        
        # Insert 2 surfaces after stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        # Retrieve surface objects
        self._retrieve_surfaces(7)
    
    def _setup_system_layout_triple3(self):
        """Setup triple lens system layout - method 3"""
        stop_surface_index = 1
        
        # Insert 6 surfaces before stop
        for _ in range(6):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        # Retrieve surface objects
        self._retrieve_surfaces(7)
    
    def _configure_lens_parameters_triple0(self, comb):
        """Configure triple lens parameters - method 0"""
        # First lens
        self.Surface_2.SemiDiameter = self.Surface_3.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_2.Radius = comb[0][2]
        self.Surface_2.Thickness = comb[0][4]
        self.Surface_2.Material = comb[0][5]
        self.Surface_3.Thickness = 2
        self.Surface_3.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Radius = comb[1][3]
        self.Surface_5.Thickness = 2
        
        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 200  # Focal plane distance
        
        self.Surface_1.Thickness = 2
        
        # Set variable parameters
        self.Surface_1.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_triple1(self, comb):
        """Configure triple lens parameters - method 1"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Thickness = 2
        self.Surface_5.Radius = comb[1][3]
        
        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 200  # Focal plane distance
        
        self.Surface_3.Thickness = 2  # Stop thickness
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_triple2(self, comb):
        """Configure triple lens parameters - method 2"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]
        
        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 200
        
        self.Surface_5.Thickness = 2  
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()

    def _configure_lens_parameters_triple3(self, comb):
        """Configure triple lens parameters - method 3"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]
        
        # Third lens
        self.Surface_5.SemiDiameter = self.Surface_6.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_5.Radius = comb[2][2]
        self.Surface_5.Thickness = comb[2][4]
        self.Surface_5.Material = comb[2][5]
        self.Surface_6.Radius = comb[2][3]
        self.Surface_6.Thickness = 2
        
        self.Surface_7.Thickness = 200
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_6.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()

class QuadraLensOptimizer(OpticalSystemOptimizer):
    def __init__(self, zosapi, the_system, rms_threshold=300, aperture=10, num_cores=8, max_iterations=30, ap=1):
        super().__init__(zosapi, the_system, rms_threshold, aperture, num_cores,max_iterations, ap )
    
    def optimize_lens_combinations(self, lens_combinations, type_code=1):
        """Optimize triple lens combinations"""
        for comb in tqdm(lens_combinations, desc="Optimizing triple lens combinations", 
                        unit="combination", miniters=len(lens_combinations), ncols=100):
            try:
                # Check focal length criteria
                if not self._check_focal_length(comb):
                    continue
                    
                # Reset system and prepare surfaces
                self._initialize_system()
                
                # Configure system
                self._configure_aperture_and_field(type_code)
                self._configure_lens_parameters_dispatcher(comb)
                
                # Optimize system and evaluate results
                self._optimize_system()
                weighted_rms = self._evaluate_results()
                
                if weighted_rms < self.rms_threshold:
                    print(f"四镜片组合：{comb}, 权重 RMS: {weighted_rms}")
                    
            except Exception as e:
                print(f"Error processing triple lens combination {comb}: {e}")
    
    def _check_focal_length(self, comb):
        """Check if triple lens focal length meets criteria"""
        lens_focals = [comb[0][6], comb[1][6], comb[2][6], comb[3][6]]
        effective_f = self._effective_focal_length(lens_focals)
        return 0 < effective_f <= 1500
    
    def _configure_lens_parameters_dispatcher(self, comb):
        """Dispatch to appropriate triple lens configuration method"""
        layout_method = getattr(self, f"_setup_system_layout_quadra{self.ap}")
        layout_method()
        
        config_method = getattr(self, f"_configure_lens_parameters_quadra{self.ap}")
        config_method(comb)
    
    def _setup_system_layout_quadra0(self):
        """Setup quadra lens system layout - method 0"""
        stop_surface_index = 1
        
        # Insert 6 surfaces for three lenses
        for _ in range(8):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        self._retrieve_surfaces(9)
    
    def _setup_system_layout_quadra1(self):
        """Setup quadra lens system layout - method 1"""
        stop_surface_index = 1
        
        # Insert 2 surfaces before stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 2
        
        # Insert 4 surfaces after stop
        for _ in range(6):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        self._retrieve_surfaces(9)

    def _setup_system_layout_quadra2(self):
        """Setup quadra lens system layout - method 2"""
        stop_surface_index = 1
        
        # Insert 4 surfaces before stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 4
        
        # Insert 2 surfaces after stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        self._retrieve_surfaces(9)
    
    def _setup_system_layout_quadra3(self):          
        """Setup quadra lens system layout - method 3"""
        stop_surface_index = 1

        for _ in range(6):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)

        stop_surface_index += 6
        
        # Insert 6 surfaces before stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        self._retrieve_surfaces(9)

    def _setup_system_layout_quadra4(self):          
        """Setup quadra lens system layout - method 4"""
        stop_surface_index = 1

        for _ in range(8):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)

        stop_surface_index += 8
        self._retrieve_surfaces(9)
    
    def _configure_lens_parameters_quadra0(self, comb):
        """Configure quadra lens parameters - method 0"""
        # First lens
        self.Surface_2.SemiDiameter = self.Surface_3.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_2.Radius = comb[0][2]
        self.Surface_2.Thickness = comb[0][4]
        self.Surface_2.Material = comb[0][5]
        self.Surface_3.Thickness = 2
        self.Surface_3.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Radius = comb[1][3]
        self.Surface_5.Thickness = 2
        
        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 2 # Focal plane distance
        
        self.Surface_1.Thickness = 2

        self.Surface_8.SemiDiameter = self.Surface_9.SemiDiameter = 0.5 * comb[3][1]
        self.Surface_8.Radius = comb[3][2]
        self.Surface_8.Thickness = comb[3][4]
        self.Surface_8.Material = comb[3][5]
        self.Surface_9.Thickness = 200
        self.Surface_9.Radius = comb[3][3]

        
        # Set variable parameters
        self.Surface_1.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
        self.Surface_9.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_quadra1(self, comb):
        """Configure quadra lens parameters - method 1"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Thickness = 2
        self.Surface_5.Radius = comb[1][3]
        
        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 2  # Focal plane distance
        
        self.Surface_3.Thickness = 2  # Stop thickness

        self.Surface_8.SemiDiameter = self.Surface_9.SemiDiameter = 0.5 * comb[3][1]
        self.Surface_8.Radius = comb[3][2]
        self.Surface_8.Thickness = comb[3][4]
        self.Surface_8.Material = comb[3][5]
        self.Surface_9.Thickness = 200
        self.Surface_9.Radius = comb[3][3]
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
        self.Surface_9.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_quadra2(self, comb):
        """Configure quadra lens parameters - method 2"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]
        
        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 2
        
        self.Surface_5.Thickness = 2  

        self.Surface_8.SemiDiameter = self.Surface_9.SemiDiameter = 0.5 * comb[3][1]
        self.Surface_8.Radius = comb[3][2]
        self.Surface_8.Thickness = comb[3][4]
        self.Surface_8.Material = comb[3][5]
        self.Surface_9.Thickness = 200
        self.Surface_9.Radius = comb[3][3]
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
        self.Surface_9.ThicknessCell.MakeSolveVariable()

    def _configure_lens_parameters_quadra3(self, comb):
        """Configure quadra lens parameters - method 3"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]
        
        # Third lens
        self.Surface_5.SemiDiameter = self.Surface_6.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_5.Radius = comb[2][2]
        self.Surface_5.Thickness = comb[2][4]
        self.Surface_5.Material = comb[2][5]
        self.Surface_6.Radius = comb[2][3]
        self.Surface_6.Thickness = 2
        
        self.Surface_7.Thickness = 2

        self.Surface_8.SemiDiameter = self.Surface_9.SemiDiameter = 0.5 * comb[3][1]
        self.Surface_8.Radius = comb[3][2]
        self.Surface_8.Thickness = comb[3][4]
        self.Surface_8.Material = comb[3][5]
        self.Surface_9.Thickness = 200
        self.Surface_9.Radius = comb[3][3]
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_6.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
        self.Surface_9.ThicknessCell.MakeSolveVariable()

    def _configure_lens_parameters_quadra4(self, comb):
        """Configure quadra lens parameters - method 4"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]
        
        # Third lens
        self.Surface_5.SemiDiameter = self.Surface_6.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_5.Radius = comb[2][2]
        self.Surface_5.Thickness = comb[2][4]
        self.Surface_5.Material = comb[2][5]
        self.Surface_6.Radius = comb[2][3]
        self.Surface_6.Thickness = 2
        
        self.Surface_9.Thickness = 200

        self.Surface_7.SemiDiameter = self.Surface_8.SemiDiameter = 0.5 * comb[3][1]
        self.Surface_7.Radius = comb[3][2]
        self.Surface_7.Thickness = comb[3][4]
        self.Surface_7.Material = comb[3][5]
        self.Surface_8.Thickness = 2
        self.Surface_8.Radius = comb[3][3]
        
        # Set variable parameters
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_6.ThicknessCell.MakeSolveVariable()
        self.Surface_8.ThicknessCell.MakeSolveVariable()
        self.Surface_9.ThicknessCell.MakeSolveVariable()


class  Macdouble(OpticalSystemOptimizer):
    def __init__(self, zosapi, the_system, rms_threshold=300, aperture=0.05, num_cores=8, max_iterations=30, ap=1):
        super().__init__(zosapi, the_system, rms_threshold, aperture, num_cores,max_iterations, ap )
    
    def optimize_lens_combinations(self, lens_combinations, type_code=3):
        """Optimize triple lens combinations"""
        for comb in tqdm(lens_combinations, desc="Optimizing triple lens combinations", 
                        unit="combination", miniters=len(lens_combinations), ncols=100):
            try:                   
                # Reset system and prepare surfaces
                self._initialize_system()
                
                # Configure system
                self._configure_aperture_and_field(type_code)
                self._configure_lens_parameters_dispatcher(comb)
                
                # Optimize system and evaluate results
                self._optimize_system()
                weighted_rms = self._evaluate_results()
                
                if weighted_rms < self.rms_threshold:
                    print(f"二镜片组合：{comb}, 权重 RMS: {weighted_rms}")
                    
            except Exception as e:
                print(f"Error processing triple lens combination {comb}: {e}")
    
    def _configure_lens_parameters_dispatcher(self, comb):
        """Dispatch to appropriate triple lens configuration method"""
        layout_method = getattr(self, f"_setup_system_layout_Macdouble{self.ap}")
        layout_method()
        
        config_method = getattr(self, f"_configure_lens_parameters_Macdouble{self.ap}")
        config_method(comb)
    
    def _setup_system_layout_Macdouble0(self):
        """Setup Macdouble system layout - method 0"""
        stop_surface_index = 1
        
        # Insert 4 surfaces for two lenses
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        # Retrieve surface objects
        self._retrieve_surfaces(5)
    
    def _setup_system_layout_Macdouble1(self):
        """Setup Macdouble system layout - method 1"""
        stop_surface_index = 1
        
        # Insert 2 surfaces before stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 2
        
        # Insert 2 surfaces after stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        # Retrieve surface objects
        self._retrieve_surfaces(5)

    def _setup_system_layout_Macdouble2(self):
        """Setup Macdouble system layout - method 2"""
        stop_surface_index = 1
        
        # Insert 4 surfaces before stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 4
        
        # Retrieve surface objects
        self._retrieve_surfaces(5)
    
    def _configure_lens_parameters_Macdouble0(self, comb):
        """Configure Macdouble lens parameters - method 0"""
        # First lens
        self.Surface_2.SemiDiameter = self.Surface_3.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_2.Radius = comb[0][2]
        self.Surface_2.Thickness = comb[0][4]
        self.Surface_2.Material = comb[0][5]
        self.Surface_3.Thickness = 2
        self.Surface_3.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Radius = comb[1][3]
        self.Surface_5.Thickness = 200
        
        self.Surface_1.Thickness = 2
        self.Surface_0.Thickness = 150
        
        # Set variable parameters
        self.Surface_0.ThicknessCell.MakeSolveVariable()
        self.Surface_1.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_triple1(self, comb):
        """Configure triple lens parameters - method 1"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Thickness = 200
        self.Surface_5.Radius = comb[1][3]
        
        self.Surface_3.Thickness = 2  # Stop thickness
        self.Surface_0.Thickness = 150  # Stop thickness
    
        # Set variable parameters
        self.Surface_0.ThicknessCell.MakeSolveVariable()
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_triple2(self, comb):
        """Configure triple lens parameters - method 2"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]
        
        self.Surface_5.Thickness = 200
        self.Surface_0.Thickness = 150    
        
        # Set variable parameters
        self.Surface_0.ThicknessCell.MakeSolveVariable()
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()


class  Mactriple(OpticalSystemOptimizer):
    def __init__(self, zosapi, the_system, rms_threshold=300, aperture=0.05, num_cores=8, max_iterations=30, ap=1):
        super().__init__(zosapi, the_system, rms_threshold, aperture, num_cores,max_iterations, ap )
    
    def optimize_lens_combinations(self, lens_combinations, type_code=3):
        """Optimize triple lens combinations"""
        for comb in tqdm(lens_combinations, desc="Optimizing triple lens combinations", 
                        unit="combination", miniters=len(lens_combinations), ncols=100):
            try:                   
                # Reset system and prepare surfaces
                self._initialize_system()
                
                # Configure system
                self._configure_aperture_and_field(type_code)
                self._configure_lens_parameters_dispatcher(comb)
                
                # Optimize system and evaluate results
                self._optimize_system()
                weighted_rms = self._evaluate_results()
                
                if weighted_rms < self.rms_threshold:
                    print(f"三镜片组合：{comb}, 权重 RMS: {weighted_rms}")
                    
            except Exception as e:
                print(f"Error processing triple lens combination {comb}: {e}")
    
    def _configure_lens_parameters_dispatcher(self, comb):
        """Dispatch to appropriate triple lens configuration method"""
        layout_method = getattr(self, f"_setup_system_layout_Mactriple{self.ap}")
        layout_method()
        
        config_method = getattr(self, f"_configure_lens_parameters_Mactriple{self.ap}")
        config_method(comb)
    
    def _setup_system_layout_Mactriple0(self):
        """Setup Mactriple system layout - method 0"""
        stop_surface_index = 1
        
        # Insert 4 surfaces for two lenses
        for _ in range(6):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        self._retrieve_surfaces(7)
    
    def _setup_system_layout_Mactriple1(self):  
        """Setup MacTriple system layout - method 1"""
        stop_surface_index = 1
        
        # Insert 2 surfaces before stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 2
        
        # Insert 2 surfaces after stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        
        self._retrieve_surfaces(7)
    
    def _setup_system_layout_Mactriple2(self):
        """Setup MacTriple system layout - method 2"""
        stop_surface_index = 1
        
        # Insert 4 surfaces before stop
        for _ in range(4):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 4
        # Insert 2 surfaces after stop
        for _ in range(2):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index + 1)
        # Retrieve surface objects
        self._retrieve_surfaces(7)

    def _setup_system_layout_Mactriple3(self):
        """Setup MacTriple system layout - method 3"""
        stop_surface_index = 1
        
        # Insert 4 surfaces before stop
        for _ in range(6):
            self.TheLDE.InsertNewSurfaceAt(stop_surface_index)
        
        stop_surface_index += 6
        # Retrieve surface objects
        self._retrieve_surfaces(7)
    
    def _configure_lens_parameters_Mactriple0(self, comb):
        """Configure Macdouble lens parameters - method 0"""
        # First lens
        self.Surface_2.SemiDiameter = self.Surface_3.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_2.Radius = comb[0][2]
        self.Surface_2.Thickness = comb[0][4]
        self.Surface_2.Material = comb[0][5]
        self.Surface_3.Thickness = 2
        self.Surface_3.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Radius = comb[1][3]
        self.Surface_5.Thickness = 2

        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 200
        
        self.Surface_1.Thickness = 2
        self.Surface_0.Thickness = 150
        
        # Set variable parameters
        self.Surface_0.ThicknessCell.MakeSolveVariable()
        self.Surface_1.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()

    def _configure_lens_parameters_triple1(self, comb):
        """Configure triple lens parameters - method 1"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_4.SemiDiameter = self.Surface_5.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_4.Radius = comb[1][2]
        self.Surface_4.Thickness = comb[1][4]
        self.Surface_4.Material = comb[1][5]
        self.Surface_5.Thickness = 2
        self.Surface_5.Radius = comb[1][3]

        # Third lens
        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 200
        
        self.Surface_3.Thickness = 2  # Stop thickness
        self.Surface_0.Thickness = 150  # Stop thickness
    
        # Set variable parameters
        self.Surface_0.ThicknessCell.MakeSolveVariable()
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_3.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
    
    def _configure_lens_parameters_triple2(self, comb):
        """Configure triple lens parameters - method 2"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]

        self.Surface_6.SemiDiameter = self.Surface_7.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_6.Radius = comb[2][2]
        self.Surface_6.Thickness = comb[2][4]
        self.Surface_6.Material = comb[2][5]
        self.Surface_7.Radius = comb[2][3]
        self.Surface_7.Thickness = 200
        
        self.Surface_5.Thickness = 2
        self.Surface_0.Thickness = 150    
        
        # Set variable parameters
        self.Surface_0.ThicknessCell.MakeSolveVariable()
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_5.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()

    def _configure_lens_parameters_triple2(self, comb):
        """Configure triple lens parameters - method 3"""
        # First lens
        self.Surface_1.SemiDiameter = self.Surface_2.SemiDiameter = 0.5 * comb[0][1]
        self.Surface_1.Radius = comb[0][2]
        self.Surface_1.Thickness = comb[0][4]
        self.Surface_1.Material = comb[0][5]
        self.Surface_2.Thickness = 2
        self.Surface_2.Radius = comb[0][3]
        
        # Second lens
        self.Surface_3.SemiDiameter = self.Surface_4.SemiDiameter = 0.5 * comb[1][1]
        self.Surface_3.Radius = comb[1][2]
        self.Surface_3.Thickness = comb[1][4]
        self.Surface_3.Material = comb[1][5]
        self.Surface_4.Thickness = 2
        self.Surface_4.Radius = comb[1][3]

        self.Surface_5.SemiDiameter = self.Surface_6.SemiDiameter = 0.5 * comb[2][1]
        self.Surface_5.Radius = comb[2][2]
        self.Surface_5.Thickness = comb[2][4]
        self.Surface_5.Material = comb[2][5]
        self.Surface_6.Radius = comb[2][3]
        self.Surface_6.Thickness = 2
        
        self.Surface_7.Thickness = 200
        self.Surface_0.Thickness = 150    
        
        # Set variable parameters
        self.Surface_0.ThicknessCell.MakeSolveVariable()
        self.Surface_2.ThicknessCell.MakeSolveVariable()
        self.Surface_4.ThicknessCell.MakeSolveVariable()
        self.Surface_6.ThicknessCell.MakeSolveVariable()
        self.Surface_7.ThicknessCell.MakeSolveVariable()
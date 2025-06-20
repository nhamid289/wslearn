class EMA:
    """
    An implementation of EMA for parameter smoothing during training.
    Implementation from https://fyubang.com/2019/06/01/ema/
    """

    def __init__(self, model, decay=0.999):
        self.model = model
        self.decay = decay
        self.shadow = {}
        self.backup = {}

        self.device = next(model.parameters()).device

        self.initialise()

    def to(self, device):
        self.device = device
        self.model.to(self.device)
        self.initialise()

    def initialise(self):
         for name, param in self.model.named_parameters():
            self.shadow[name] = param.data.clone().to(self.device)

    def update(self):
        """
        Update the smoothed parameters.
        """
        for name, param in self.model.named_parameters():
            new_average = (1.0 - self.decay) * param.data + self.decay * self.shadow[name]
            self.shadow[name] = new_average.clone().to(self.device)

        for name, buffer in self.model.named_buffers():
            self.shadow[name] = buffer.clone().to(self.device)

    def apply_shadow(self):
        """
        Replace the model parameters with the EMA shadow. Stores a backup of
        the original parameters.
        """
        for name, param in self.model.named_parameters():
            self.backup[name] = param.data.clone().to(self.device)
            param.data = self.shadow[name].clone().to(self.device)

    def restore(self):
        """
        Restore the model to the backup parameters
        """
        for name, param in self.model.named_parameters():
            param.data = self.backup[name].clone().to(self.device)
        self.backup = {}

    def load_model(self, ema_model):
        """
        Load parameters from another model. Replaces the existing parameters
        """
        for name, param in ema_model.named_parameters():
            self.shadow[name] = param.data.clone().to(self.device)




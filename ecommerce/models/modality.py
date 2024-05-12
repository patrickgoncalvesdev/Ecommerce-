from django.db import models
from rest_framework import serializers
from decimal import Decimal


class Modality(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    number_separator = models.BooleanField(default=False)
    max_len_input_guess = models.IntegerField(
        default=10,
        verbose_name="Qtd. máxima de dígitos",
        help_text="Máximo de caracteres para o input do palpite",
    )
    min_len_input_guess = models.IntegerField(
        default=2,
        verbose_name="Qtd. mínima de dígitos",
        help_text="Mínimo de caracteres para o input do palpite",
    )
    max_quantity_guess = models.IntegerField(
        default=100,
        verbose_name="Qtd. máxima de palpites",
        help_text="Máximo de palpites por aposta",
    )
    max_guess_value = models.IntegerField(
        default=25,
        verbose_name="Valor máximo do palpite",
        help_text="Número máximo do palpite",
    )
    max_bet_value = models.DecimalField(
        max_digits=10,
        verbose_name="Máximo valor de aposta",
        decimal_places=2,
        default=100,
        help_text="Valor máximo da aposta",
    )
    min_bet_value = models.DecimalField(
        max_digits=10,
        verbose_name="Mínimo valor de aposta",
        decimal_places=2,
        default=1,
        help_text="Valor mínimo da aposta",
    )
    big_guess = models.BooleanField(default=False)
    placements = models.ManyToManyField(
        "Placing", related_name="modalities", blank=True, through="PlacingModality"
    )
    ref = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="referrals",
        help_text="Referência para modalidades que são variações de outras modalidades. (INV)",
    )

    class Meta:
        verbose_name = "Modalidade"
        verbose_name_plural = "Modalidades"

    def __str__(self) -> str:
        return self.name

    def validate_guesses(self, guesses: list[str]):
        if len(guesses) > self.max_quantity_guess:
            raise serializers.ValidationError(
                {
                    "guesses": f"A modalidade selecionada requer menos que {self.max_quantity_guess} palpites."
                }
            )
        for guess in guesses:
            if len(guess) > self.max_len_input_guess:
                raise serializers.ValidationError(
                    {
                        "guesses": f"A modalidade selecionada requer menos que {self.max_len_input_guess} caracteres por palpite."
                    }
                )
            if len(guess) < self.min_len_input_guess:
                raise serializers.ValidationError(
                    {
                        "guesses": f"A modalidade selecionada requer pelo menos {self.min_len_input_guess} caracteres por palpite."
                    }
                )
            if self.max_guess_value > 0:
                if int(guess) > self.max_guess_value:
                    raise serializers.ValidationError(
                        {
                            "guesses": f"O palpite {guess} é maior que o valor máximo permitido para a modalidade {self.name}."
                        }
                    )

    def validate_bet_value(self, value: Decimal):
        if value <= 0:
            raise serializers.ValidationError(
                {"bet_value": "O valor da aposta deve ser maior que zero."}
            )
        if value > self.max_bet_value:
            raise serializers.ValidationError(
                {
                    "bet_value": f"O valor da aposta é maior que o valor máximo permitido para a modalidade {self.name}."
                }
            )
        if value < self.min_bet_value:
            raise serializers.ValidationError(
                {
                    "bet_value": f"O valor da aposta é menor que o valor mínimo permitido para a modalidade {self.name}."
                }
            )

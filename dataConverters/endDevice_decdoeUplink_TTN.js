function decodeUplink(input) {
  var result = "";

  for (var i = 0; i < input.bytes.length; i++) {
        result += String.fromCharCode(input.bytes[i]);
  }

  try {
        // Intentamos interpretar el texto como JSON
        var json = JSON.parse(result);

        return {
            data: json,          // Si es JSON válido, devuelve sus campos
            warnings: [],
            errors: []
        };
  } catch (e) { // Si no es JSON válido, devolvemos el raw text 
                return {
            data: {
              raw_text: result,  // Texto recibido sin parsear
              bytes: input.bytes
          },
          warnings: [],
          errors: ["No se pudo parsear el mensaje como JSON: " + e.message]
    };
  }
}
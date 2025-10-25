import { FormEvent, useState } from "react";
import axios from "axios";
import { useMutation, useQueryClient } from "@tanstack/react-query";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const NewCallForm = () => {
  const client = useQueryClient();
  const [open, setOpen] = useState(false);
  const [formState, setFormState] = useState({
    caller_id: "",
    description: "",
    operator_id: 1,
  });

  const mutation = useMutation({
    mutationFn: async () => {
      await axios.post(`${API_BASE}/llamadas`, {
        caller_id: formState.caller_id,
        description: formState.description,
        operator_id: formState.operator_id,
      });
    },
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["incidentes"] });
      setFormState({ caller_id: "", description: "", operator_id: 1 });
      setOpen(false);
    },
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    mutation.mutate();
  };

  if (!open) {
    return (
      <button className="new-call" onClick={() => setOpen(true)}>
        Registrar llamada
      </button>
    );
  }

  return (
    <form className="new-call__form" onSubmit={handleSubmit}>
      <label>
        Teléfono
        <input
          required
          value={formState.caller_id}
          onChange={(event) => setFormState((prev) => ({ ...prev, caller_id: event.target.value }))}
        />
      </label>
      <label>
        Descripción
        <textarea
          rows={3}
          value={formState.description}
          onChange={(event) => setFormState((prev) => ({ ...prev, description: event.target.value }))}
        />
      </label>
      <div className="form-actions">
        <button type="button" onClick={() => setOpen(false)}>
          Cancelar
        </button>
        <button type="submit" disabled={mutation.isPending}>
          Guardar
        </button>
      </div>
    </form>
  );
};

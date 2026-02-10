import { Nav } from "../../components/Nav";

const pending = [
  { name: "Arun Kumar", purpose: "Parent Meeting", time: "10:40 AM" },
  { name: "Medline Vendor", purpose: "Supply Delivery", time: "10:44 AM" },
  { name: "Priya Raj", purpose: "Event Entry", time: "10:49 AM" }
];

export default function StaffPage() {
  return (
    <main className="container">
      <Nav />
      <h1>Staff Approval Queue</h1>
      <table className="table card">
        <thead>
          <tr>
            <th>Visitor</th>
            <th>Purpose</th>
            <th>Requested</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {pending.map((item) => (
            <tr key={`${item.name}-${item.time}`}>
              <td>{item.name}</td>
              <td>{item.purpose}</td>
              <td>{item.time}</td>
              <td style={{ display: "flex", gap: ".5rem" }}>
                <button className="btn btn-success">Approve</button>
                <button className="btn btn-danger">Reject</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

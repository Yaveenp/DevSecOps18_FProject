import React from 'react';
import { Line } from 'react-chartjs-2';
import sampleData from '../../data/sampleData';

const Graphs: React.FC = () => {
    const data = {
        labels: sampleData.labels,
        datasets: [
            {
                label: 'Sample Data',
                data: sampleData.values,
                fill: false,
                backgroundColor: 'rgba(75,192,192,0.4)',
                borderColor: 'rgba(75,192,192,1)',
            },
        ],
    };

    return (
        <div>
            <h2>Data Visualization</h2>
            <Line data={data} />
        </div>
    );
};

export default Graphs;